import pandas as pd
import matplotlib.pyplot as plt


# load the data
file_path = 'input_force.csv'
data = pd.read_csv(file_path)

# extract the coordinate (x,y), and the energy z
x = data.iloc[:, 0]
y = data.iloc[:, 1]
z = data.iloc[:, 2]

# create 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_trisurf(x, y, z, cmap='viridis')

# Sex axis titles and tick labels
ax.set_xlabel('Ne-H (Å)', fontname='Arial', fontsize=18, fontweight='bold', labelpad=10)
ax.set_ylabel('H-H (Å)' , fontname='Arial', fontsize=18, fontweight='bold', labelpad=10)
ax.set_zlabel('Energy (Hartree)', fontname='Arial', fontsize=18, fontweight='bold', labelpad=10)

# set the font and size of tick labels
for label in ax.get_xticklabels():
    label.set_fontname('Arial')
    # label.set_fontsize(18)
    label.set_fontweight('bold')

for label in ax.get_yticklabels():
    label.set_fontname('Arial')
    # label.set_fontsize(18)
    label.set_fontweight('bold')

for label in ax.get_zticklabels():
    label.set_fontname('Arial')
    # label.set_fontsize(18)
    label.set_fontweight('bold')

# show the plot
plt.show()
