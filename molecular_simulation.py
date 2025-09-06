"""
Molecular dynamics simulation driven by learned PES.

Molecular dynamics simulation based on trained potential energy surface (PES).
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from model import NeuralNetwork
from config import get_config
from utils import ensure_dir

# ---------- Helpers for picking correct arch & weights ----------
ACTIVATIONS = {"Mish", "ReLU", "LeakyReLU", "ELU", "GELU"}
STEM_REGEX = re.compile(r"^(\d+)-(\d+)-([A-Za-z]+)$")
TS_SUFFIX = re.compile(r"-\d{8}-\d{6}$")  # -YYYYMMDD-HHMMSS

def _parse_stem_to_arch(stem_no_ts: str):
    """
    stem format: "<num_layers>-<hidden_dim>-<activation>"
    """
    m = STEM_REGEX.match(stem_no_ts)
    if not m:
        return None
    num_layers = int(m.group(1))
    hidden_dim = int(m.group(2))
    act = m.group(3)
    if act not in ACTIVATIONS:
        return None
    return {"num_layers": num_layers, "hidden_dim": hidden_dim, "activation_function": act}

def _latest_pth_in_dir(dirpath: str):
    try:
        pths = [
            os.path.join(dirpath, f)
            for f in os.listdir(dirpath)
            if f.endswith(".pth") and os.path.isfile(os.path.join(dirpath, f))
        ]
        if not pths:
            return None
        pths.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        return pths[0]
    except Exception:
        return None
# ---------------------------------------------------------------


def run_simulation(
    config_name: str,
    model_dir: str,
    steps: int = 60000,
    dt: float = 10e-19,
    init_x1: float = 3.0,
    init_x2: float = 0.0,
    init_x3: float = -1.108,
    init_v1: float = -20000,
    init_v2: float = 0.0,
    init_v3: float = 0.0,
):
    """
    Run an MD trajectory using gradients from the neural PES.

    Use neural network potential energy gradients to advance MD trajectory.
    """
    # 1) Read base config and override structure based on directory name (parse after removing timestamp suffix)
    cfg = get_config(config_name)
    ensure_dir(model_dir)

    dir_base = os.path.basename(os.path.normpath(model_dir))
    stem_no_ts = TS_SUFFIX.sub("", dir_base)        # Remove -YYYYMMDD-HHMMSS
    arch = _parse_stem_to_arch(stem_no_ts)
    if arch:
        cfg["num_layers"] = arch["num_layers"]
        cfg["hidden_dim"] = arch["hidden_dim"]
        cfg["activation_function"] = arch["activation_function"]

    input_dim = cfg["input_dim"]
    output_dim = cfg["output_dim"]
    hidden_dim = cfg["hidden_dim"]
    num_layers = cfg["num_layers"]
    activation_name = cfg["activation_function"]

    # 2) Select weights to load: prioritize cfg['save_model_path'], otherwise latest .pth in directory
    preferred_path = os.path.join(model_dir, cfg.get("save_model_path", "model.pth"))
    if os.path.exists(preferred_path):
        model_path = preferred_path
    else:
        cand = _latest_pth_in_dir(model_dir)
        if cand is None:
            raise FileNotFoundError(f"No .pth file found under {model_dir}")
        model_path = cand

    # 3) Build model and load matching weights
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = NeuralNetwork(input_dim, hidden_dim, num_layers, output_dim, activation_name).to(device)

    # Use map_location to be compatible with CPU/GPU scenarios
    state = torch.load(model_path, map_location=device)
    model.load_state_dict(state)
    model.eval()

    # ---------- Physical constants and initial conditions ----------
    F = 4.3597e-8
    m = 1.661e-27
    m1, m2, m3 = 20.1797, 1.0079, 1.0079
    m11, m21, m31 = m1 * m / F, m2 * m / F, m3 * m / F

    x1, x2, x3 = init_x1, init_x2, init_x3
    v1, v2, v3 = init_v1, init_v2, init_v3

    time_list, rlist, coordinates_list, potential_list, Elist = [], [], [], [], []

    # ---------- Time advancement ----------
    for i in range(steps):
        r12 = x1 - x2
        r23 = x2 - x3
        time_list.append(i * dt)
        coordinates_list.append([x1, x2, x3])
        rlist.append([r12, r23])

        # Enable grad for input, use neural potential gradients as forces
        input_tensor = torch.tensor([[r12, r23]], dtype=torch.float32, requires_grad=True, device=device)
        output = model(input_tensor)                   # [1, 1] or [1], depending on your network output implementation
        potential_list.append(float(output.detach().cpu().item()))

        # If trajectory goes beyond training domain, end early
        if r12 < 0 or r12 > 4.0 or r23 < 0 or r23 > 3.99:
            print("break")
            break

        # Total energy (note output is tensor, convert to float for storage below)
        E = (
            output * 8.314
            + 0.5 * m1 * m * abs(v1 ** 2) * 10e19 / 1.609
            + 0.5 * m2 * m * abs(v2 ** 2) * 10e19 / 1.609
            + 0.5 * m3 * m * abs(v3 ** 2) * 10e19 / 1.609
        )
        Elist.append(float(E.detach().cpu().item()))

        # Calculate forces (gradient of potential with respect to r)
        model.zero_grad(set_to_none=True)
        if input_tensor.grad is not None:
            input_tensor.grad.zero_()
        output.backward()
        predictions = input_tensor.grad / 0.529
        F1 = -predictions[0][0]
        F2 = predictions[0][0] - predictions[0][1]
        F3 = predictions[0][1]

        # Velocity-position update (simple explicit integration, consistent with original version)
        x1 = float(x1 + v1 * dt * 1e10)
        x2 = float(x2 + v2 * dt * 1e10)
        x3 = float(x3 + v3 * dt * 1e10)
        a1, a2, a3 = F1 / m11, F2 / m21, F3 / m31
        v1 = v1 + float(a1) * dt
        v2 = v2 + float(a2) * dt
        v3 = v3 + float(a3) * dt

    # ---------- Save CSV trajectory ----------
    df = pd.DataFrame(coordinates_list, columns=["Ne(x1)", "H(x2)", "H(x3)"])
    df.insert(0, "Time", time_list)
    df.insert(1, "Potential", potential_list)
    csv_path = f"{model_dir}/simulation_results.csv"
    df.to_csv(csv_path, index=False)

    # ---------- XYZ export ----------
    df_xyz = pd.read_csv(csv_path)
    trajectory_path = f"{model_dir}/{config_name}_trajectory.xyz"
    with open(trajectory_path, "w") as f:
        for _, row in df_xyz.iterrows():
            f.write("3\n")
            f.write(f"Time = {row['Time']:.5e} seconds\n")
            f.write(f"Ne {row['Ne(x1)']} 0 0\n")
            f.write(f"H {row['H(x2)']} 0 0\n")
            f.write(f"H {row['H(x3)']} 0 0\n")
    print("XYZ file created successfully: " + trajectory_path)

    # ---------- Contour + MD trajectory ----------
    r12_values = np.linspace(0.5, 4.0, 100)
    r23_values = np.linspace(0.5, 4.0, 100)
    R12, R23 = np.meshgrid(r12_values, r23_values)
    Potential = np.zeros_like(R12, dtype=np.float32)

    # No gradient needed when evaluating potential, no_grad speeds up
    with torch.no_grad():
        for i in range(R12.shape[0]):
            for j in range(R12.shape[1]):
                input_tensor = torch.tensor([[R12[i, j], R23[i, j]]], dtype=torch.float32, device=device)
                out = model(input_tensor)
                Potential[i, j] = float(out.detach().cpu().item())

    rlist1 = np.array(rlist)
    plt.figure(figsize=(12, 9))
    plt.contour(R12, R23, Potential, levels=100, cmap="viridis")
    if len(rlist1) > 0:
        plt.scatter(rlist1[:, 0], rlist1[:, 1], color="red")
    plt.xlabel("Ne-H", fontsize=24, fontname="Arial", fontweight="bold")
    plt.ylabel("H-H", fontsize=24, fontname="Arial", fontweight="bold")
    plt.title("MD Simulation", fontsize=28, fontname="Arial", fontweight="bold")
    plt.xticks(fontsize=18, fontname="Arial")
    plt.yticks(fontsize=18, fontname="Arial")
    plt.savefig(f"{model_dir}/{config_name}_MD.png")

    # ---------- Energy curve ----------
    plt.figure(figsize=(12, 9))
    plt.plot(range(len(Elist)), Elist, marker='o', linestyle='-', color='b', label='Line')
    plt.title('Total Energy')
    plt.xlabel('iteration')
    plt.ylabel('Total Energy')
    plt.savefig(f"{model_dir}/{config_name}_Energy.png")

    return {
        "csv_path": csv_path,
        "xyz_path": trajectory_path,
        "energy_plot": f"{model_dir}/{config_name}_Energy.png",
        "md_plot": f"{model_dir}/{config_name}_MD.png",
    }
