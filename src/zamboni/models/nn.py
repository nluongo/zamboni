import torch
import torch.nn as nn

# Simple neural network classifier
class SimpleNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

class EmbeddingNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes, num_embed_features, num_embed_categories, embed_dim):
        super(EmbeddingNN, self).__init__()
        # Only embedding teams, so use common embedding for home and away
        self.num_embed_features = num_embed_features
        self.num_classes = num_classes
        self.team_embedding = nn.Embedding(num_embed_categories, embed_dim)
        continuous_inputs = input_size - num_embed_features
        category_inputs = num_embed_features * embed_dim
        linear_inputs = continuous_inputs + category_inputs
        self.fc1 = nn.Linear(linear_inputs, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x, x_cat):
        embeddings = [self.team_embedding(x_cat[:,i]) for i in range(self.num_embed_features)]
        x = torch.cat([x]+embeddings, 1)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x
