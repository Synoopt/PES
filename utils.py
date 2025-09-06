"""
Utility helpers: model I/O, logging, visualization, metrics.

Utility function collection: model I/O, logging, visualization and evaluation metrics.
"""

import torch
import logging
from datetime import datetime
from torch.utils.tensorboard import SummaryWriter
import numpy as np
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import os


def ensure_dir(path: str):
    """
    Create directory if absent.

    Create directory if it doesn't exist.
    """
    os.makedirs(path, exist_ok=True)


 


def load_model(model, path):
    """
    Load a state dict into the given model.

    Load weights from specified path into the given model.
    """
    model.load_state_dict(torch.load(path))
    model.eval()
    logging.info(f"Model loaded from {path}")
    return model


def setup_logging(experiment_name):
    """
    Create a TensorBoard SummaryWriter.

    Create TensorBoard writer.
    """
    current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_dir = f"logs/{current_time}_{experiment_name}"
    writer = SummaryWriter(log_dir)
    return writer


def log_metrics(writer, metrics, step, prefix="Train"):
    """
    Log training or validation metrics to TensorBoard.

    Write training/validation metrics to TensorBoard.
    """
    for key, value in metrics.items():
        writer.add_scalar(f"{prefix}/{key}", value, step)


def visualize_model(model, data, savepath, savepath2, saverocpath, atom1="H", atom2="H", atom3="Ne"):
    """
    Generate 3 figures: scatter-of-true-vs-pred, 3D surface, 2D contour.

    Generate 3 plots: true-vs-predicted scatter, 3D surface, 2D contour.
    
    Args:
        model: trained neural network model
        data: pandas DataFrame with x, y, z1 columns
        savepath: path to save 3D surface plot
        savepath2: path to save 2D contour plot
        saverocpath: path to save true vs predicted plot
        atom1: first atom type (default: "H")
        atom2: second atom type (default: "H") 
        atom3: third atom type (default: "Ne")
    """
    # Draw the ROC curve
    x = data['x']
    y = data['y']
    x_roc = np.array([x.to_numpy(), y.to_numpy()]).T
    x_roc_tensor = torch.tensor(x_roc, dtype=torch.float32)
    model.eval()
    # predict
    with torch.no_grad():  # excluding the gradient
        y_roc_tensor = model(x_roc_tensor)
    # convert the result to numpy array
    y_roc = y_roc_tensor.numpy()
    print()
    # Visualize the reliability of predictions.
    plt.figure()
    plt.scatter(data['z1'], y_roc, alpha=0.7, label='Predicted vs True')
    plt.plot([data['z1'].min(), data['z1'].max()], [data['z1'].min(), data['z1'].max()], 'k--', lw=2, label='Ideal Fit')
    plt.xlabel('True Values')
    plt.ylabel('Predicted Values')
    plt.title('True vs Predicted Values')
    plt.legend()
    plt.savefig(saverocpath)
    # Create a grid to predict **z** values.
    xp = np.linspace(0.5, 4.0, 1000)
    yp = np.linspace(0.5, 4.0, 1000)
    xp, yp = np.meshgrid(xp, yp)
    X_pred = np.array([xp.ravel(), yp.ravel()]).T
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    X_pred_tensor = torch.tensor(X_pred, dtype=torch.float32).to(device)

    # predict
    with torch.no_grad():  # excluding the gradient
        y_pred_tensor = model(X_pred_tensor).cpu()

    # convert the result to numpy array
    y_pred = y_pred_tensor.numpy()
    # visualize
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(data['x'], data['y'], data['z1'], c='g', marker='.')
    # ax.plot_surface(data['x'], data['y'], data['z1'].to_numpy().reshape(data['x'].shape), alpha=0.7)
    ax.plot_surface(xp, yp, y_pred.reshape(xp.shape), alpha=0.7)

    # Use atom types for better labels
    ax.set_xlabel(f'{atom3}-{atom2} (Å)', fontname='Arial', fontsize=18, fontweight='bold', labelpad=10)
    ax.set_ylabel(f'{atom2}-{atom1} (Å)', fontname='Arial', fontsize=18, fontweight='bold', labelpad=10)
    ax.set_zlabel('Energy (Hartree)', fontname='Arial', fontsize=18, fontweight='bold', labelpad=10)

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

    plt.savefig(savepath)
    plt.close()

    fig = plt.figure()
    ax = fig.add_subplot()
    ax.contour(xp, yp, y_pred.reshape(xp.shape), 30)
    
    # Use atom types for better labels in 2D plot
    ax.set_xlabel(f'{atom3}-{atom2} (Å)', fontname='Arial', fontsize=18, fontweight='bold')
    ax.set_ylabel(f'{atom2}-{atom1} (Å)', fontname='Arial', fontsize=18, fontweight='bold')
    ax.set_title(f'{atom1}-{atom2}-{atom3} Potential Energy Surface', fontname='Arial', fontsize=16, fontweight='bold')
    
    plt.savefig(savepath2)
    plt.close()


def accuracy(model, data):
    """
    Compute R-squared on provided dataframe.

    Compute R^2 on provided dataframe.
    """
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    X_pred = np.array([data['x'].to_numpy(), data['y'].to_numpy()]).T
    X_pred_tensor = torch.tensor(X_pred, dtype=torch.float32).to(device)

    # Make predictions
    with torch.no_grad():
        y_pred_tensor = model(X_pred_tensor).cpu()

    y_pred = y_pred_tensor.numpy()

    r_squared = r2_score(data['z1'], y_pred)

    return r_squared
