"""
Data loading helpers.

Data loading utilities: read from CSV and build PyTorch DataLoader.
"""

import pandas as pd
from torch.utils.data import TensorDataset, DataLoader
import torch

def load_data(file_path, shuffle=True):
    """
    Load training data from CSV into a DataLoader.

    Load training data from CSV and build DataLoader.

    The CSV is expected to contain columns: x, y, z1, z2, z3, z4.
    Expected CSV columns: x, y, z1, z2, z3, z4.
    """
    data = pd.read_csv(file_path)
    X = data[['x', 'y']]
    y = data[['z1','z2','z3','z4']]
    # Convert to torch tensors
    X_train = torch.tensor(X.to_numpy(), dtype=torch.float32, requires_grad=True)
    y_train = torch.tensor(y.to_numpy(), dtype=torch.float32)
    train_data = TensorDataset(X_train, y_train)
    # Return one sample at a time (no batching concept)
    train_loader = DataLoader(train_data, shuffle=shuffle)

    return train_loader, data
    
