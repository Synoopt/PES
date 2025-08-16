"""
Neural network model definition.

神经网络模型定义：多层感知机，支持按名称安全解析激活函数（如 Mish、ReLU、LeakyReLU）。
"""

import torch
import torch.nn as nn

class NeuralNetwork(nn.Module):
    def __init__(
        self,
        input_dim,
        hidden_dim,
        num_layers,
        output_dim,
        activation_name,
        dropout_ratio: float = 0.0,
    ):
        """
        Initialize a feed-forward network.

        初始化前馈网络。

        Args:
            input_dim (int): number of input features / 输入特征维度
            hidden_dim (int): hidden layer width / 隐藏层维度
            num_layers (int): number of hidden layers / 隐藏层层数
            output_dim (int): output dimension / 输出维度
            activation_name (str): activation name in torch.nn / 激活函数名称（torch.nn 中）
            dropout_ratio (float): optional dropout rate / 可选 Dropout 比例
        """
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        super(NeuralNetwork, self).__init__()

        if num_layers < 1:
            raise ValueError("Number of layers must be at least 1")

        self.layers = nn.ModuleList()  # create a list of modules to store all the hidden layers.

        # Add the first hidden layer that accepts the input dimensions.
        first_layer = nn.Linear(input_dim, hidden_dim)
        self.layers.append(first_layer)

        # Add additional hidden layers where both the input and output dimensions are set to `hidden_dim`.
        for _ in range(1, num_layers):
            layer = nn.Linear(hidden_dim, hidden_dim)
            self.layers.append(layer)

        # Resolve activation by name safely (e.g., "Mish", "ReLU", "LeakyReLU").
        # 按名称安全解析激活函数。
        if not hasattr(nn, activation_name):
            raise ValueError(f"Unknown activation function: {activation_name}")
        self.activation = getattr(nn, activation_name)()

        # Optionally add a Dropout layer, which is enabled only if `dropout_ratio` is greater than 0.
        if dropout_ratio > 0:
            self.dropout = nn.Dropout(dropout_ratio)
        else:
            self.dropout = None

        # The output layer
        self.output_layer = nn.Linear(hidden_dim, output_dim)
        #nn.init.kaiming_uniform_(self.output_layer.weight, nonlinearity='leaky_relu')

    def forward(self, x):
        """
        Forward pass through stacked layers and output head.

        前向传播：依次通过堆叠的隐藏层与输出层。
        """
        # Pass through each layer to perform operations
        for layer in self.layers:
            x = layer(x).to(x.device)
            x = self.activation(x)
            if self.dropout:
                x = self.dropout(x)

        # Pass the output layer
        x = self.output_layer(x)
        return x
