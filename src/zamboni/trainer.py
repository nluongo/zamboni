import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import os
import logging
from glob import glob
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from zamboni.models.simplenn import SimpleNN, EmbeddingNN
from zamboni.dataset import ZamboniDataset
import matplotlib.pyplot as plt

class TrainingDataLoader():
    """ Load data for NN training """
    def __init__(self, data_path):
        self.data_path = data_path

    def load_parquet(self):
        """
        Read data from parquet file into dataframe
        """
        data = pd.read_parquet(self.data_path)
        data = data[data['homeTeamID'] != -1]
        data = data[data['awayTeamID'] != -1]
        self.data = data
        
    def define_columns(self, target_column='outcome', categorical_columns=['homeTeamID', 'awayTeamID']):
        """
        Define which column is the label and which will use categorical embedding

        param: target_column: Column holding labels
        param: categorical_columns: Columns for categorical embedding
        """
        self.all_columns = self.data.columns.tolist()
        self.target_column = target_column
        self.categorical_columns = categorical_columns
        self.noscale_columns = [self.target_column] + self.categorical_columns

    def split_data(self, test_size=0.2, random_state=42):
        """
        Split into train and test sets

        param: test_size: Percentage of dataset for testing
        param: random_state: Seed for randomizing
        """
        self.train_data, self.test_data = train_test_split(self.data, test_size=test_size, random_state=random_state, shuffle=False)

    def scale_data(self, scaler=None):
        """
        Apply scaling

        param: scaler: Scaler class
        """
        if not scaler:
            self.scaler = StandardScaler()
        else:
            self.scaler = scaler
        train_features = self.scaler.fit_transform(self.train_data.drop(columns=self.noscale_columns))
        test_features = self.scaler.transform(self.test_data.drop(columns=self.noscale_columns))

        # Recreate the train and test DataFrames with scaled features
        self.train_data_scaled = pd.DataFrame(train_features)
        self.test_data_scaled = pd.DataFrame(test_features)
        for column in self.noscale_columns:
            self.train_data_scaled[column] = self.train_data[column].values
            self.test_data_scaled[column] = self.test_data[column].values

    def create_datasets(self):
        self.train_dataset = ZamboniDataset(self.train_data_scaled, self.target_column, self.categorical_columns) 
        logging.info(f'{len(self.train_dataset)} training samples')
        self.test_dataset = ZamboniDataset(self.test_data_scaled, self.target_column, self.categorical_columns)
        logging.info(f'{len(self.test_dataset)} testing samples')

    def create_dataloaders(self):
        self.train_loader = DataLoader(self.train_dataset, batch_size=32, shuffle=True)
        self.test_loader = DataLoader(self.test_dataset, batch_size=32, shuffle=False)

class Trainer():
    def __init__(self, model, optimizer, train_loader, test_loader, load_epoch=0, load_loss=0):
        self.model = model
        self.optimizer = optimizer
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.load_epoch = load_epoch
        self.load_loss = load_loss

    def train(self, criterion=None, train_epochs=10):
        if criterion is None:
            criterion = nn.CrossEntropyLoss()

        # Training loop
        for epoch in range(self.load_epoch, self.load_epoch+train_epochs):
            self.model.train()
            running_loss = 0.0
            for inputs, cat_inputs, labels in self.train_loader:
                print(inputs)
                print(cat_inputs)
                self.optimizer.zero_grad()
                outputs = self.model(inputs, cat_inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()
                running_loss += loss.item()

            self.model.eval()
            running_test_loss = 0.0
            with torch.no_grad():
                for inputs, cat_inputs, labels in self.test_loader:
                    outputs = self.model(inputs, cat_inputs)
                    #test_outputs = model(test_inputs)
                    loss = criterion(outputs, labels)
                    running_test_loss += loss.item()
            
            print(f'Epoch [{epoch+1}/{train_epochs}], Train loss: {running_loss/len(self.train_loader):.4f}, Test loss: {running_test_loss/len(self.test_loader):.4f}')
        self.end_epoch = epoch
        self.end_loss = running_test_loss / len(self.test_loader)

        print("Training complete.")
        

class ModelInitializer():
    def __init__(self, model_dir_path, model_class, data):
        self.model_dir_path = model_dir_path
        self.model_class = model_class
        self.data = data

    def get_model(self):
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
        if self.model_class == 'EmbeddingNN':
            # Define the model, loss function, and optimizer
            input_size = self.data.shape[1] - 1
            hidden_size = 8
            num_classes = 2
            num_embed_features = 2 # Home and away
            num_teams = 33
            num_embed_categories = num_teams
            embed_dim = 5
            model = EmbeddingNN(input_size, hidden_size, num_classes, num_embed_features, num_embed_categories, embed_dim)
        self.model = model

    def initialize_optimizer(self):
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)

    def get_latest_checkpoint(self):
        files = glob(os.path.join(self.model_dir_path,'*'))
        last_updated = max(files, key=os.path.getmtime)
        return last_updated


    def save_model(self, save_dir, epoch, loss):
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'loss': loss
            }, f'data/{save_dir}/epoch{epoch}.tar')
        
#model.eval()
#criterion = nn.CrossEntropyLoss(reduction='none')
#
#train_labels = []
#train_outputs = []
#test_labels = []
#test_outputs = []
#
#for inputs, cat_inputs, labels in train_loader:
#    outputs = model(inputs, cat_inputs)
#    train_labels += labels.tolist()
#    train_outputs += outputs.tolist()
#
#for inputs, cat_inputs, labels in test_loader:
#    outputs = model(inputs, cat_inputs)
#    test_labels += labels.tolist()
#    test_outputs += outputs.tolist()
#
#plt.hist(train_labels)
#plt.savefig('tester.png')


