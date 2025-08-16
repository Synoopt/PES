"""
Data loading helpers.

数据加载工具：从 CSV 读取并构建 PyTorch DataLoader。
"""

import pandas as pd
from torch.utils.data import TensorDataset, DataLoader
import torch

def load_data(file_path, shuffle=True):
    """
    Load training data from CSV into a DataLoader.

    从 CSV 读取训练数据并构建 DataLoader。

    The CSV is expected to contain columns: x, y, z1, z2, z3, z4.
    期望 CSV 包含列：x, y, z1, z2, z3, z4。
    """
    data = pd.read_csv(file_path)
    X = data[['x', 'y']]
    y = data[['z1','z2','z3','z4']]
    # 转换为torch张量
    X_train = torch.tensor(X.to_numpy(), dtype=torch.float32, requires_grad=True)
    y_train = torch.tensor(y.to_numpy(), dtype=torch.float32)
    train_data = TensorDataset(X_train, y_train)
    # 每次返回一个样本（无批处理概念）
    train_loader = DataLoader(train_data, shuffle=shuffle)

    return train_loader, data
    
