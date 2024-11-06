import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from models.simplenn import SimpleNN

# Custom Dataset class to handle parquet data
class ParquetDataset(Dataset):
    def __init__(self, data, target_column):
        self.features = data.drop(columns=[target_column]).values
        self.labels = data[target_column].values

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        x = torch.tensor(self.features[idx], dtype=torch.float32)
        y = torch.tensor(self.labels[idx], dtype=torch.long)
        return x, y

# Load parquet file into a Pandas DataFrame
data = pd.read_parquet('~/Code/zamboni/data/games.parquet')

# Define target column name
target_column = 'outcome'

# Split the data into train and test sets
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

# Standardize the features
#scaler = StandardScaler()
#train_features = scaler.fit_transform(train_data.drop(columns=[target_column]))
#test_features = scaler.transform(test_data.drop(columns=[target_column]))
train_features = train_data.drop(columns=[target_column])
test_features = test_data.drop(columns=[target_column])

# Recreate the train and test DataFrames with scaled features
train_data_scaled = pd.DataFrame(train_features, columns=train_data.columns[:-1])
train_data_scaled[target_column] = train_data[target_column].values
test_data_scaled = pd.DataFrame(test_features, columns=test_data.columns[:-1])
test_data_scaled[target_column] = test_data[target_column].values

# Create Dataset objects
train_dataset = ParquetDataset(train_data_scaled, target_column)
test_dataset = ParquetDataset(test_data_scaled, target_column)

# DataLoader for batching
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

# Define the model, loss function, and optimizer
input_size = train_features.shape[1]
hidden_size = 64
num_classes = len(data[target_column].unique())
model = SimpleNN(input_size, hidden_size, num_classes)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
epochs = 10
for epoch in range(epochs):
    model.train()
    running_loss = 0.0
    for inputs, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    
    print(f'Epoch [{epoch+1}/{epochs}], Loss: {running_loss/len(train_loader):.4f}')

print("Training complete.")

