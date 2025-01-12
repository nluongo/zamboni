import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from models.simplenn import SimpleNN, EmbeddingNN
import matplotlib.pyplot as plt

# Custom Dataset class to handle parquet data
class ZamboniDataset(Dataset):
    def __init__(self, data, target_column, cat_features=None):
        self.feature_data = data.drop(columns=[target_column])
        self.features = self.feature_data.values
        self.cont_features = self.feature_data.drop(columns=cat_features).values
        self.cat_features = data[cat_features].values
        self.labels = data[target_column].values

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        x_cont = torch.tensor(self.cont_features[idx], dtype=torch.float32)
        x_cat = torch.tensor(self.cat_features[idx], dtype=torch.long)
        y = torch.tensor(self.labels[idx], dtype=torch.long)
        if self.cat_features is not None:
            return x_cont, x_cat, y
        else:
            return x_cont, y

# Load parquet file into a Pandas DataFrame
data = pd.read_parquet('~/Code/zamboni/data/games.parquet')
data = data[data['homeTeamID'] != -1]
data = data[data['awayTeamID'] != -1]

# Define target column name
all_columns = data.columns.tolist()
target_column = 'outcome'
categorical_columns = ['homeTeamID', 'awayTeamID']
noscale_columns = [target_column] + categorical_columns
#scale_columns = all_columns - noscale_columns

# Split the data into train and test sets
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

num_teams = int(train_data['homeTeamID'].nunique()) + 5

# Standardize the features
scaler = StandardScaler()
train_features = scaler.fit_transform(train_data.drop(columns=noscale_columns))
test_features = scaler.transform(test_data.drop(columns=noscale_columns))
#train_features = train_data.drop(columns=noscale_columns)
#test_features = test_data.drop(columns=noscale_columns)

# Recreate the train and test DataFrames with scaled features
train_data_scaled = pd.DataFrame(train_features)
test_data_scaled = pd.DataFrame(test_features)
for column in noscale_columns:
    train_data_scaled[column] = train_data[column].values
    test_data_scaled[column] = test_data[column].values

# Create Dataset objects
train_dataset = ZamboniDataset(train_data_scaled, target_column, categorical_columns) 
print(len(train_dataset))
test_dataset = ZamboniDataset(test_data_scaled, target_column, categorical_columns)
print(len(test_dataset))

# DataLoader for batching
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

# Define the model, loss function, and optimizer
input_size = train_data.shape[1] - 1
#input_size = 9
print('input_size: ',input_size)
hidden_size = 256
num_classes = len(data[target_column].unique())
num_embed_features = 2 # Embedding each team
num_embed_categories = num_teams
embed_dim = 10
#model = SimpleNN(input_size, hidden_size, num_classes)
model = EmbeddingNN(input_size, hidden_size, num_classes, num_embed_features, num_embed_categories, embed_dim)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
epochs = 10
for epoch in range(epochs):
    model.train()
    running_loss = 0.0
    for inputs, cat_inputs, labels in test_loader:
        optimizer.zero_grad()
        outputs = model(inputs, cat_inputs)
        #outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    model.eval()
    running_test_loss = 0.0
    with torch.no_grad():
        for inputs, cat_inputs, labels in train_loader:
            outputs = model(inputs, cat_inputs)
            #test_outputs = model(test_inputs)
            loss = criterion(outputs, labels)
            running_test_loss += loss.item()
    
    print(f'Epoch [{epoch+1}/{epochs}], Train loss: {running_loss/len(train_loader):.4f}, Test loss: {running_test_loss/len(test_loader):.4f}')

model.eval()
criterion = nn.CrossEntropyLoss(reduction='none')

train_labels = []
train_outputs = []
test_labels = []
test_outputs = []

for inputs, cat_inputs, labels in train_loader:
    outputs = model(inputs, cat_inputs)
    train_labels += labels.tolist()
    train_outputs += outputs.tolist()

for inputs, cat_inputs, labels in test_loader:
    outputs = model(inputs, cat_inputs)
    test_labels += labels.tolist()
    test_outputs += outputs.tolist()

plt.hist(train_labels)
plt.savefig('tester.png')

print("Training complete.")

