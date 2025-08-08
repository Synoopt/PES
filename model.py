import torch
import torch.nn as nn

class NeuralNetwork(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, output_dim, activation_function,dropout_ratio=0.0):
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

        # define the activation function
        self.leaky_relu = eval(activation_function)

        # Optionally add a Dropout layer, which is enabled only if `dropout_ratio` is greater than 0.
        if dropout_ratio > 0:
            self.dropout = nn.Dropout(dropout_ratio)
        else:
            self.dropout = None

        # The output layer
        self.output_layer = nn.Linear(hidden_dim, output_dim)
        #nn.init.kaiming_uniform_(self.output_layer.weight, nonlinearity='leaky_relu')

    def forward(self, x):
        # Pass through each layer to perform operations
        for layer in self.layers:
            x = layer(x).to(x.device)
            x = self.leaky_relu(x)
            if self.dropout:
                x = self.dropout(x)

        # Pass the output layer
        x = self.output_layer(x)
        return x
