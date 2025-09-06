import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
from matplotlib import rcParams
from model import NeuralNetwork
from config import get_config

# Set the global font and size
rcParams['font.family'] = 'Arial'
rcParams['font.weight'] = 'bold'
rcParams['axes.labelweight'] = 'bold'
rcParams['axes.labelsize'] = 12
rcParams['xtick.labelsize'] = 10
rcParams['ytick.labelsize'] = 10

# Set the file path
path = "3-64"

# read the data
data = pd.read_csv("input_force.csv")

# get config from config.py
config = get_config(path)

input_dim = config['input_dim']
output_dim = config['output_dim']
hidden_dim = config['hidden_dim']
num_layers = config['num_layers']
activation_function = "nn." + config['activation_function'] + "()"

# Instantiate the network.
model = NeuralNetwork(input_dim, hidden_dim, num_layers, output_dim, activation_function)

# Load the model weights.
model.load_state_dict(torch.load(path + "/" + path + ".pth"))

# pretreatment of data
X_real = data[['x', 'y']].values
y_real = data['z1'].values
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
X_real_tensor = torch.tensor(X_real, dtype=torch.float32).to(device)

# predict using model
with torch.no_grad():
    y_pred_tensor = model(X_real_tensor).cpu()

# Convert the prediction results to a NumPy array.
y_pred = y_pred_tensor.numpy().flatten()

# Calculate the difference between the predicted values and the actual values.
error = y_pred - y_real

# Calculate the mean deviation and the maximum deviation.
mean_error = np.mean(np.abs(error))
max_error = np.max(np.abs(error))

print(f"Mean deviation: {mean_error:.4f}")
print(f"Maximum deviation: {max_error:.4f}")

# Draw the contour plot
plt.figure(figsize=(10, 8))
contour = plt.tricontourf(X_real[:, 0], X_real[:, 1], error, levels=14, cmap='RdBu')
colorbar = plt.colorbar(contour)
colorbar.set_label('Prediction Error (Hartree)', fontsize=24, fontname='Arial')
colorbar.ax.tick_params(labelsize=18)
for label in colorbar.ax.get_yticklabels():
    label.set_fontname('Arial')

plt.xlabel('Ne-H (Å)', fontsize=24, fontname="Arial", fontweight="bold")
plt.ylabel('H-H (Å)', fontsize=24, fontname="Arial", fontweight="bold")
plt.xticks(fontsize=18, fontname="Arial")
plt.yticks(fontsize=18, fontname="Arial")
plt.grid(True)
plt.show()
