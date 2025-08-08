import pandas as pd
from torch.utils.data import TensorDataset, DataLoader
import torch

def load_data(file_path, shuffle=True):
    data = pd.read_csv(file_path)
    X = data[['x', 'y']]
    y = data[['z1','z2','z3','z4']]
    # 转换为torch张量
    X_train = torch.tensor(X.to_numpy(), dtype=torch.float32, requires_grad=True)
    y_train = torch.tensor(y.to_numpy(), dtype=torch.float32)
    train_data = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_data, shuffle=shuffle)

    return train_loader, data
    
