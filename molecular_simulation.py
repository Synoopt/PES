"""
Molecular dynamics simulation driven by learned PES.

基于已训练势能面（PES）的分子动力学模拟。
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

    使用神经网络势能的梯度推进 MD 轨迹。
    """
    # 1) 读取基础 cfg，并根据目录名覆盖结构（去掉末尾时间戳后再解析）
    cfg = get_config(config_name)
    ensure_dir(model_dir)

    dir_base = os.path.basename(os.path.normpath(model_dir))
    stem_no_ts = TS_SUFFIX.sub("", dir_base)        # 把 -YYYYMMDD-HHMMSS 去掉
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

    # 2) 选择要加载的权重：优先 cfg['save_model_path']，否则目录里最新 .pth
    preferred_path = os.path.join(model_dir, cfg.get("save_model_path", "model.pth"))
    if os.path.exists(preferred_path):
        model_path = preferred_path
    else:
        cand = _latest_pth_in_dir(model_dir)
        if cand is None:
            raise FileNotFoundError(f"No .pth file found under {model_dir}")
        model_path = cand

    # 3) 构建模型并加载匹配的权重
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = NeuralNetwork(input_dim, hidden_dim, num_layers, output_dim, activation_name).to(device)

    # 用 map_location 兼容 CPU/GPU 场景
    state = torch.load(model_path, map_location=device)
    model.load_state_dict(state)
    model.eval()

    # ---------- 物理常数与初始条件 ----------
    F = 4.3597e-8
    m = 1.661e-27
    m1, m2, m3 = 20.1797, 1.0079, 1.0079
    m11, m21, m31 = m1 * m / F, m2 * m / F, m3 * m / F

    x1, x2, x3 = init_x1, init_x2, init_x3
    v1, v2, v3 = init_v1, init_v2, init_v3

    time_list, rlist, coordinates_list, potential_list, Elist = [], [], [], [], []

    # ---------- 时间推进 ----------
    for i in range(steps):
        r12 = x1 - x2
        r23 = x2 - x3
        time_list.append(i * dt)
        coordinates_list.append([x1, x2, x3])
        rlist.append([r12, r23])

        # 对输入开 grad，用神经势的梯度作为力
        input_tensor = torch.tensor([[r12, r23]], dtype=torch.float32, requires_grad=True, device=device)
        output = model(input_tensor)                   # [1, 1] 或 [1]，取决于你的网络输出实现
        potential_list.append(float(output.detach().cpu().item()))

        # 若轨迹超出训练域，提前结束
        if r12 < 0 or r12 > 4.0 or r23 < 0 or r23 > 3.99:
            print("break")
            break

        # 总能量（注意这里 output 是张量，下面取 float 存储）
        E = (
            output * 8.314
            + 0.5 * m1 * m * abs(v1 ** 2) * 10e19 / 1.609
            + 0.5 * m2 * m * abs(v2 ** 2) * 10e19 / 1.609
            + 0.5 * m3 * m * abs(v3 ** 2) * 10e19 / 1.609
        )
        Elist.append(float(E.detach().cpu().item()))

        # 计算力（potential 对 r 的梯度）
        model.zero_grad(set_to_none=True)
        if input_tensor.grad is not None:
            input_tensor.grad.zero_()
        output.backward()
        predictions = input_tensor.grad / 0.529
        F1 = -predictions[0][0]
        F2 = predictions[0][0] - predictions[0][1]
        F3 = predictions[0][1]

        # 速度-位置更新（简单显式积分，与原版保持一致）
        x1 = float(x1 + v1 * dt * 1e10)
        x2 = float(x2 + v2 * dt * 1e10)
        x3 = float(x3 + v3 * dt * 1e10)
        a1, a2, a3 = F1 / m11, F2 / m21, F3 / m31
        v1 = v1 + float(a1) * dt
        v2 = v2 + float(a2) * dt
        v3 = v3 + float(a3) * dt

    # ---------- 保存 CSV 轨迹 ----------
    df = pd.DataFrame(coordinates_list, columns=["Ne(x1)", "H(x2)", "H(x3)"])
    df.insert(0, "Time", time_list)
    df.insert(1, "Potential", potential_list)
    csv_path = f"{model_dir}/simulation_results.csv"
    df.to_csv(csv_path, index=False)

    # ---------- XYZ 导出 ----------
    df_xyz = pd.read_csv(csv_path)
    trajectory_path = f"{model_dir}/{config_name}_trajectory.xyz"
    with open(trajectory_path, "w") as f:
        for _, row in df_xyz.iterrows():
            f.write("3\n")
            f.write(f"Time = {row['Time']:.5e} seconds\n")
            f.write(f"Ne {row['Ne(x1)']} 0 0\n")
            f.write(f"H {row['H(x2)']} 0 0\n")
            f.write(f"H {row['H(x3)']} 0 0\n")
    print("XYZ file created successfully：" + trajectory_path)

    # ---------- 等高线 + MD 轨迹 ----------
    r12_values = np.linspace(0.5, 4.0, 100)
    r23_values = np.linspace(0.5, 4.0, 100)
    R12, R23 = np.meshgrid(r12_values, r23_values)
    Potential = np.zeros_like(R12, dtype=np.float32)

    # 评价势能时不需要梯度，no_grad 提速
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

    # ---------- 能量曲线 ----------
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
