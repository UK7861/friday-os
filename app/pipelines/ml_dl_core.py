import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class MLPipeline:
    def __init__(self):
        self.scaler = StandardScaler()

    def train_simple_regressor(self, X, y):
        # Placeholder for production ML pipeline
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        # Model logic here...
        return "Model trained successfully"

class DeepLearningCore(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
    
    def forward(self, x):
        return self.net(x)
