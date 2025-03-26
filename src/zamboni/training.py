from datetime import timedelta
from glob import glob
import os
import logging
import pandas as pd
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
import torch.optim as optim

from zamboni.data_management import ZamboniData
from zamboni.models.nn import EmbeddingNN

class Trainer():
    """ Train and evaluate models """
    def __init__(self, model, optimizer, criterion=None, load_epoch=0, load_loss=0):
        self.model = model
        self.optimizer = optimizer
        self.load_epoch = load_epoch
        self.load_loss = load_loss
        if criterion is None:
            if self.model.num_classes > 1:
                self.criterion = nn.CrossEntropyLoss()
            else:
                self.criterion = nn.BCEWithLogitsLoss()

    def calculate_loss(self, outputs, labels):
        """
        Calculate loss for model outputs

        :param outputs: Model predictions
        :param labels: Truth labels
        :returns: Loss value
        """
        if self.model.num_classes == 1:
            labels = labels.float()
            outputs = torch.squeeze(outputs, 1)
        loss = self.criterion(outputs, labels)
        return loss

    def eval(self, loader):
        """
        Evaluate model on test data
        
        :param loader: DataLoader for test data
        :returns: Average loss, outputs, labels
        """
        self.model.eval()
        total_loss = 0
        all_labels = torch.tensor([])
        all_outputs = torch.tensor([])
        with torch.no_grad():
            for inputs, cat_inputs, labels in loader:
                outputs = self.model(inputs, cat_inputs)
                all_outputs = torch.concat([all_outputs, outputs])
                all_labels = torch.concat([all_labels, labels])
                loss = self.calculate_loss(outputs, labels)
                total_loss += loss.item()
        loss_per_sample = total_loss / len(loader)
        return loss_per_sample, all_outputs, all_labels

    def train(self, train_loader, test_loader=None, train_epochs=10, log_step=True):
        """
        Train model on given dataloader

        :param train_loader: DataLoader for training data
        :param test_loader: DataLoader for test data, optional
        :param train_epochs: Number of epochs to train
        :param log_step: Flag to log
        """
        # Training loop
        for epoch in range(self.load_epoch, self.load_epoch+train_epochs):
            self.model.train()
            running_loss = 0.0
            for inputs, cat_inputs, labels in train_loader:
                self.optimizer.zero_grad()
                outputs = self.model(inputs, cat_inputs)
                loss = self.calculate_loss(outputs, labels)
                loss.backward()
                self.optimizer.step()
                running_loss += loss.item()

            test_loss = 0
            if test_loader:
                test_loss, _, _ = self.eval(test_loader)
 
            if log_step:
                logging.info(f'Epoch [{epoch+1}/{train_epochs}], Train loss: {running_loss/len(train_loader):.4f}, Test loss: {test_loss:.4f}')
        self.end_epoch = epoch
        self.end_loss = test_loss

class ModelInitializer():
    """ Create, save, and load models """
    def __init__(self, model_dir_path, model_class, column_tracker):
        self.model_dir_path = model_dir_path
        self.model_class = model_class
        self.column_tracker = column_tracker

    def get_model(self):
        """
        Get model, optimizer, and load checkpoint if available else create them
        
        :returns: Model, optimizer, epoch, loss
        """
        self.initialize_model()
        self.initialize_optimizer()
        epoch = 0
        loss = 0
        if os.path.exists(self.model_dir_path):
            checkpoint_path = self.get_latest_checkpoint()
            print(checkpoint_path)
            logging.info(f'Model file found at {checkpoint_path}')
            logging.info(f'Attempting to load..')
            try:
                checkpoint = torch.load(checkpoint_path, weights_only=True)
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
                epoch = checkpoint['epoch']
                loss = checkpoint['loss']
            except:
                raise ValueError(f'Unable to load. Exiting.')
        else:
            logging.info(f'Creating and training new model.')
        self.model.train()
        return self.model, self.optimizer, epoch, loss

    def initialize_model(self):
        """
        Create model with architecture consistent with features and target
        """
        if self.model_class == 'EmbeddingNN':
            # Define the model, loss function, and optimizer
            input_size = len(self.column_tracker.inputs)
            hidden_size = 8
            num_classes = 2
            num_embed_features = 2 # Home and away
            num_teams = 33
            num_embed_categories = num_teams
            embed_dim = 5
            model = EmbeddingNN(input_size, hidden_size, num_classes, num_embed_features, num_embed_categories, embed_dim)
        self.model = model

    def initialize_optimizer(self):
        """
        Create optimizer
        """
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)

    def get_latest_checkpoint(self):
        """
        Get latest checkpoint file in model directory

        :returns: Path to latest checkpoint
        """
        files = glob(os.path.join(self.model_dir_path,'*'))
        last_updated = max(files, key=os.path.getmtime)
        return last_updated

    def save_model(self, save_dir, epoch, loss):
        """
        Save model, optimizer, loss, and epoch
        
        :param save_dir: Directory to save model
        :param epoch: Epoch number
        :param loss: Loss value
        """
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'loss': loss
            }, f'data/{save_dir}/epoch{epoch}.tar')

class SequentialStrategy():
    """ Run a sequential strategy for training and predicting """
    def __init__(self, data, trainer, start_date=None, end_date=None):
        self.data = data
        self.column_tracker = data.column_tracker
        self.trainer = trainer
        self.start_date = start_date
        self.end_date = end_date
        self.yesterdays_games = None
        self.yesterdays_preds = None
        self.yesterdays_date = None
        self.day_delta = timedelta(days=1)

    def run(self):
        """
        For each day, train on previous day's games and predict current day's games
        
        :returns: Trainer object, all predictions, all labels
        """
        # Determine first and last dates present in game data
        first_game = self.data.data.iloc[0]
        last_game = self.data.data.iloc[-1]
        first_date = pd.to_datetime(first_game['datePlayed'])
        last_date = pd.to_datetime(last_game['datePlayed'])

        # Use start and end dates if provided, otherwise use first and last dates
        if not self.start_date:
            self.start_date = first_date
        self.current_date = self.start_date
        if not self.end_date:
            self.end_date = last_date

        all_labels = torch.tensor([], dtype=torch.float32)
        all_preds = torch.tensor([], dtype=torch.float32)
        while self.current_date <= self.end_date:
            scaler = StandardScaler()
            fit_today = True
            if self.current_date != self.start_date:
                fit_today = False

                # Scale based on all data seen by the network so far
                all_prev_games = self.data.select_by_date(self.start_date, self.yesterdays_date)
                all_pred_data = ZamboniData(all_prev_games, self.column_tracker)
                all_pred_data.scale_data(scaler=scaler, fit=True)

                if len(self.yesterdays_games) > 0:
                    yesterdays_data = ZamboniData(self.yesterdays_games, self.column_tracker)
                    yesterdays_data.scale_data(scaler=scaler, fit=False, transform=True)
                    yesterdays_data.readd_noscale_columns()
                    yesterdays_data.create_dataset()
                    yesterdays_data.create_dataloader()
                    self.trainer.train(yesterdays_data.loader, log_step=False)

            todays_games = self.data.select_by_date(self.current_date, self.current_date)
            if len(todays_games) > 0:
                todays_data = ZamboniData(todays_games, self.column_tracker)
                todays_data.scale_data(scaler=scaler, fit=fit_today)
                todays_data.readd_noscale_columns()
                todays_data.create_dataset()
                todays_data.create_dataloader()
                _, todays_preds, todays_labels = self.trainer.eval(todays_data.loader)

            all_labels = torch.cat([all_labels, todays_labels])
            all_preds = torch.cat([all_preds, todays_preds])

            self.yesterdays_games = todays_games
            self.yesterdays_preds = todays_preds
            self.yesterdays_date = self.current_date

            self.current_date += self.day_delta

        if len(all_preds.shape) > 1:
            all_preds = torch.squeeze(all_preds, 1)

        return self.trainer, all_preds, all_labels

class ResultsAnalyzer():
    """ Analyze trained model results """
    def __init__(self, preds, labels):
        self.preds = preds
        self.labels = labels
        self.preds_prob = torch.sigmoid(self.preds)
        self.preds_bin = torch.round(self.preds_prob)

    def get_accuracy(self, threshold=0.5):
        """
        Calculate accuracy of model predictions with variable cutoff

        :param threshold: Cutoff for model predictions
        :returns: Accuracy of model predictions
        """
        preds_prob_abs = torch.abs(self.preds_prob)
        above_mask = preds_prob_abs > threshold
        below_mask = preds_prob_abs < (1 - threshold)
        conf_mask = above_mask | below_mask
        preds_bin = self.preds_bin[conf_mask]
        labels = self.labels[conf_mask]

        if len(preds_bin) == 0:
            return 0

        preds_correct = torch.sum(preds_bin == labels)
        num_preds = labels.shape[0]
        accuracy = preds_correct / num_preds

        return accuracy
