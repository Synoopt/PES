import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from model import NeuralNetwork
from config import get_config

# Set the path for the model directory.
path = "2-32-filtered"

# Read the data
data = pd.read_csv("input_force_filtered2.csv")

config=get_config(path)

input_dim = config['input_dim']
output_dim = config['output_dim']
hidden_dim = config['hidden_dim']
num_layers = config['num_layers']
activation_function = "nn."+config['activation_function']+"()"

# Instantiate the neural network.
model = NeuralNetwork(input_dim, hidden_dim, num_layers, output_dim, activation_function)

# Molecular Dynamics Simulation
# **F** and **m** are two constants, **x1** and **x3** are the coordinates of two atoms, specifically Ne and H, respectively. **v1** and **v3** are the initial velocities of the two atoms, and **a1** and **a3** are the initial accelerations of the two atoms.
# **m1** and **m3** are the relative atomic masses of three atoms. **m11** and **m31** are the modified relative masses of the three atoms, adjusted based on constants for simulation purposes. **ai** represents the duration of each simulation.
model.load_state_dict(torch.load(path + "/" + path + ".pth"))

# Initiate the parameters.
F = 4.3597e-8
x1 = 3.0
x2 = 0
x3 = -1.108
v1 = -20000
v2 = 0
v3 = 0
a1 = 0
a2 = 0
a3 = 0
m = 1.661e-27
m1 = 20.1797
m2 = 1.0079
m3 = 1.0079
m11 = m1*m/F
m21 = m2*m/F
m31 = m3*m/F
ai = 10e-19

# Initialize storage lists.
time_list = []
rlist = []
coordinates_list = []
potential_list = []
Elist = []

for i in range(0,60000):
    r12 = x1-x2
    r23 = x2-x3
    time_list.append(i * ai)
    coordinates_list.append([x1, x2, x3])
    rlist.append([r12, r23])
    input = torch.tensor([[r12, r23]], dtype=torch.float32, requires_grad=True)
    output = model(input)
    potential_list.append(output.item())
    if r12 < 0 or r12 > 4.0 or r23 < 0 or r23 > 3.99:
        print('break')
        break
    E = output*8.314 + 0.5*m1*m*abs(v1**2)*10e19/1.609+0.5*m2*m*abs(v2**2)*10e19/1.609+0.5*m3*m*abs(v3**2)*10e19/1.609
    E1 = E.detach().numpy()[0][0]
    Elist.append(E1)
    output.backward()
    predictions = input.grad/0.529
    F1 = -predictions[0][0]
    F2 = predictions[0][0]-predictions[0][1]
    F3 = predictions[0][1]
    x1 = x1+v1*ai*1e10
    x2 = x2+v2*ai*1e10
    x3 = x3+v3*ai*1e10

    x1 = float(x1)
    x2 = float(x2)
    x3 = float(x3)

    a1 = F1/m11
    a2 = F2/m21
    a3 = F3/m31
    v1 = v1+a1*ai
    v2 = v2+a2*ai
    v3 = v3+a3*ai

# Generate csv file
df = pd.DataFrame(coordinates_list, columns=["Ne(x1)", "H(x2)", "H(x3)"])
df.insert(0, "Time", time_list)
df.insert(1, "Potential", potential_list)
csv_path = path + "/simulation_results.csv"
df.to_csv(csv_path, index=False)

# Read csv file
df = pd.read_csv(csv_path)

# Convert to xyz file
trajectory_path = path + "/" + path + "_trajectory.xyz"
with open(trajectory_path, "w") as f:
    for index, row in df.iterrows():
        f.write("3\n")  # 3 atoms in total
        f.write(f"Time = {row['Time']:.5e} seconds\n")
        # Write the information for each atom, where **x1** corresponds to the Ne atom, and **x2** and **x3** correspond to the H atoms.
        f.write(f"Ne {row['Ne(x1)']} 0 0\n")  # Assume the **y** and **z** coordinates are 0.
        f.write(f"H {row['H(x2)']} 0 0\n")
        f.write(f"H {row['H(x3)']} 0 0\n")
print("XYZ file created successfully：" + trajectory_path)

# Generate contour plot
r12_values = np.linspace(0.5, 4.0, 100)
r23_values = np.linspace(0.5, 4.0, 100)
R12, R23 = np.meshgrid(r12_values, r23_values)
Potential = np.zeros_like(R12)

for i in range(R12.shape[0]):
    for j in range(R12.shape[1]):
        input = torch.tensor([[R12[i, j], R23[i, j]]], dtype=torch.float32)
        output = model(input)
        Potential[i, j] = output.item()

# Generate the MD simulation track
rlist1 = np.array(rlist)

# draw the contour plot
plt.figure(figsize=(12, 9))
cp = plt.contour(R12, R23, Potential, levels=100, cmap="viridis")
plt.scatter(rlist1[:, 0], rlist1[:, 1], color="red")
plt.xlabel("Ne-H", fontsize=24, fontname="Arial", fontweight="bold")
plt.ylabel("H-H", fontsize=24, fontname="Arial", fontweight="bold")
plt.title("MD Simulation", fontsize=28, fontname="Arial", fontweight="bold")
plt.xticks(fontsize=18, fontname="Arial")
plt.yticks(fontsize=18, fontname="Arial")
plt.savefig(path + "/" + path + "_MD.png")

#Draw the curve of the energy change
plt.figure(figsize=(12, 9))
Elen = len(Elist)
plt.plot(range(Elen),Elist, marker='o', linestyle='-', color='b', label='Line')
plt.title('Total Energy')
plt.xlabel('iteration')
plt.ylabel('Total Energy')
plt.savefig(path + "/" + path + "_Energy.png")
