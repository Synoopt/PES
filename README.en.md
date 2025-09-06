## PES Project Guide

For single language reading, please see:
- Chinese: `README.zh-CN.md`
- English: `README.en.md`

---

### Features

- **Train**: Train neural network potential energy surface using CSV data
- **Visualize**: Generate true-vs-predicted scatter plots, 3D surfaces and 2D contours
- **Simulate**: Run simple molecular dynamics simulation using trained PES gradients
- **Logging**: TensorBoard metrics visualization
- **Atom Configuration**: Customize three-atom systems with automatic chart labeling

---

### Environment Setup

1) Use virtual environment (recommended)
```
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2) Install dependencies
```
pip install -r requirements.txt
```

For GPU support, ensure you have the proper CUDA-enabled PyTorch version installed.

---

### Quick Start

Command Line Interface (CLI):
```
# Train (Unix/macOS)
./run.sh train --config 2-64 --data input_force_filtered.csv --out 2-64
# Train (Windows)
run.bat train --config 2-64 --data input_force_filtered.csv --out 2-64

# Visualize (Unix/macOS)
./run.sh visualize --config 2-64 --data input_force_filtered.csv --model-dir 2-64
# Visualize (Windows)
run.bat visualize --config 2-64 --data input_force_filtered.csv --model-dir 2-64

# Simulate (Unix/macOS)
./run.sh simulate --config 2-64 --model-dir 2-64 --steps 50000
# Simulate (Windows)
run.bat simulate --config 2-64 --model-dir 2-64 --steps 50000

# List configurations (Unix/macOS)
./run.sh list-configs
# List configurations (Windows)
run.bat list-configs
```

Graphical User Interface (GUI):
```
# Unix/macOS
./run.sh gui
# Windows
run.bat gui
# Visit: http://localhost:8501
```

The GUI supports Chinese/English language switching: select Language/语言 in the sidebar to switch interface text in real-time.

**Atom Configuration**: In the sidebar "Global Settings" section, you can configure three atom types for your molecular system:
- **First Atom**: Select from 20 common elements (H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca)
- **Second Atom**: Choose the second atom type
- **Third Atom**: Choose the third atom type

The selected atom types automatically apply to:
- Chart axis labels (e.g., X-axis: Ne-H (Å), Y-axis: H-H (Å))
- Plot titles (e.g., "H-H-Ne Potential Energy Surface")
- All generated visualizations

### Cross-platform Execution

The project provides two execution scripts:
- `run.sh`: For Unix/Linux/macOS systems
- `run.bat`: For Windows systems

Both scripts support the same commands and arguments.

---

### Data Format

Training CSV must contain the following columns: `x`, `y`, `z1`, `z2`, `z3`, `z4`.
- `x, y`: Input coordinates
- `z1`: Main target value
- `z2..z4`: Target gradients (for gradient supervision)

---

### Configuration

See `config.py`. `DEFAULT_CONFIG_NAME` specifies the default configuration. Each configuration includes:
- `hidden_dim`, `num_layers`, `activation_function`
- `learning_rate`, `epochs`, `patience`, `min_delta` (per-sample training, equivalent to batch size=1)
- `train_data_path`
- Visualization output filenames (`saveaxpath`, `saveaxpath2`, `assesspath`) and model save name `save_model_path`

Most parameters can be overridden via CLI/GUI.

---

### Code Structure

- `main.py`: Command line entry point (train/visualize/simulate/list-configs)
- `gui.py`: Streamlit graphical interface with atom configuration system
- `model.py`: Neural network model definition (activation functions resolved by name)
- `train.py`: Training loop (early stopping, learning rate scheduling, TensorBoard logging)
- `data_loader.py`: CSV data loading to PyTorch DataLoader
- `utils.py`: Visualization, evaluation, logging and utility functions with atom-aware labeling
- `loss.py`: Custom loss function (value MSE + gradient MSE)
- `molecular_simulation.py`: Simple molecular dynamics simulation based on potential energy gradients
- `config.py`: Configuration registry and default hyperparameters
- `mkdir.py`: Directory creation utility

---

### Training

CLI example:
```
# Unix/macOS
./run.sh train --config 2-64 --data input_force_filtered.csv --out 2-64 \
  --epochs 800 --patience 60 --lr 0.0005 --activation ReLU
# Windows
run.bat train --config 2-64 --data input_force_filtered.csv --out 2-64 \
  --epochs 800 --patience 60 --lr 0.0005 --activation ReLU
```

Training logs are generated in the `logs/` directory for TensorBoard:
```
tensorboard --logdir logs
```

---

### Visualization

After training, the following files will be generated:
- True-vs-predicted consistency plot: `assess.png`
- 3D PES surface: `ax.png`
- 2D contour: `ax2.png`

**Atom Configuration Integration**: When using the GUI, all charts automatically use the configured atom types:
- **3D Surface Plot**: X-axis = {atom3}-{atom2} (Å), Y-axis = {atom2}-{atom1} (Å)
- **2D Contour Plot**: Title shows {atom1}-{atom2}-{atom3} Potential Energy Surface
- **Axis Labels**: Automatically generated based on atom types (e.g., Ne-H, H-H)

See the commands above for usage.

---

### Molecular Simulation

Example:
```
# Unix/macOS
./run.sh simulate --config 2-64 --model-dir 2-64 --steps 60000 --dt 1e-18 \
  --x1 3.0 --x2 0.0 --x3 -1.108 --v1 -20000 --v2 0 --v3 0
# Windows
run.bat simulate --config 2-64 --model-dir 2-64 --steps 60000 --dt 1e-18 \
  --x1 3.0 --x2 0.0 --x3 -1.108 --v1 -20000 --v2 0 --v3 0
```

Outputs include:
- Trajectory CSV: `simulation_results.csv`
- XYZ file: `<config>_trajectory.xyz`
- MD contour with trajectory: `*_MD.png`
- Total energy curve: `*_Energy.png`

---

### Frequently Asked Questions (FAQ)

- CUDA unavailable? Install CUDA-enabled PyTorch or use CPU mode.
- Blank visualization? Check if data column names and ranges are correct (x, y ∈ [0.5, 4.0]).
- Low R2 score? Try increasing network width/layers, adjusting learning rate or training epochs.

---

### License

Unless otherwise specified, default to this project's LICENSE terms.

