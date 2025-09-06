# -*- coding: utf-8 -*-
"""
连续空间的神经网络势能面最小值搜索（多起点 + Adam + LBFGS）
- 自动从 state_dict 推断 MLP 结构：layers.N.* + output_layer.*

用法：
1) 将模型 state_dict 保存为 ./3-32-Mish-20250829-121636/3-32-Mish-20250829-121636.pth
2) 可选：./input_force_filtered.csv（仅用于参考，不再读取范围）
3) 在 PES-main 目录下运行： python minimumCheck.py
"""

import json
import re
import torch
import torch.nn as nn
import pandas as pd

# ---------- 配置 ----------
csv_path = "input_force_filtered.csv"
model_path = "3-32-Mish-20250829-121636/3-32-Mish-20250829-121636.pth"
seed_count = 48
adam_steps = 600
lbfgs_steps = 50
adam_lr = 0.05

# ---------- 动态模型 ----------
def _infer_linear_shapes_from_state_dict(state_dict):
    """
    从 state_dict 推断结构：
      layers.0.weight [h1, in_dim]
      layers.1.weight [h2, h1]
      ...
      output_layer.weight [out_dim, h_last]
    返回: in_dim, hidden_dims(list), out_dim
    """
    layer_idxs = []
    for k in state_dict.keys():
        m = re.match(r"layers\.(\d+)\.weight$", k)
        if m:
            layer_idxs.append(int(m.group(1)))
    layer_idxs.sort()
    if not layer_idxs:
        raise ValueError("state_dict 中未找到 'layers.N.weight'。")

    # 第一层
    w0 = state_dict[f"layers.{layer_idxs[0]}.weight"]
    h1, in_dim = w0.shape
    hidden_dims = [h1]

    # 其余隐藏层
    for i in layer_idxs[1:]:
        wi = state_dict[f"layers.{i}.weight"]
        hi, prev = wi.shape
        hidden_dims.append(hi)

    # 输出层
    if "output_layer.weight" not in state_dict:
        raise ValueError("缺少 'output_layer.weight'。")
    w_out = state_dict["output_layer.weight"]
    out_dim, last_hidden = w_out.shape
    if last_hidden != hidden_dims[-1]:
        raise ValueError(f"输出层输入维度({last_hidden}) != 最后一层隐藏维度({hidden_dims[-1]})。")

    return in_dim, hidden_dims, out_dim

class InferredMishMLP(nn.Module):
    """
    根据 state_dict 推断出的 MLP：
      x -> Linear(in, h1) -> Mish -> ... -> Linear(hk, out)
    """
    def __init__(self, in_dim, hidden_dims, out_dim=1):
        super().__init__()
        self.layers = nn.ModuleList()
        prev = in_dim
        for h in hidden_dims:
            self.layers.append(nn.Linear(prev, h))
            prev = h
        self.output_layer = nn.Linear(prev, out_dim)
        self.act = nn.Mish()

    def forward(self, x):
        for lin in self.layers:
            x = self.act(lin(x))
        x = self.output_layer(x)
        return x

def load_model(path: str) -> nn.Module:
    obj = torch.load(path, map_location="cpu")
    if isinstance(obj, nn.Module):
        model = obj
        model.eval()
        return model
    # state_dict 模式
    state_dict = obj
    in_dim, hidden_dims, out_dim = _infer_linear_shapes_from_state_dict(state_dict)
    model = InferredMishMLP(in_dim, hidden_dims, out_dim)
    model.load_state_dict(state_dict, strict=True)
    model.eval()
    return model

# ---------- 优化工具 ----------
def param_to_xy(u: torch.Tensor, x_bounds: torch.Tensor, y_bounds: torch.Tensor):
    sx = torch.sigmoid(u[0])
    sy = torch.sigmoid(u[1])
    x = x_bounds[0] + (x_bounds[1] - x_bounds[0]) * sx
    y = y_bounds[0] + (y_bounds[1] - y_bounds[0]) * sy
    return x, y

@torch.no_grad()
def grid_seed_samples(n: int, x_bounds: torch.Tensor, y_bounds: torch.Tensor, device="cpu"):
    xs = torch.empty(n, device=device).uniform_(x_bounds[0], x_bounds[1])
    ys = torch.empty(n, device=device).uniform_(y_bounds[0], y_bounds[1])
    return torch.stack([xs, ys], dim=1)

def invert_sigmoid(z: torch.Tensor, eps=1e-7):
    z = torch.clamp(z, eps, 1 - eps)
    return torch.log(z) - torch.log(1 - z)

def refine_one_start(
    model: nn.Module,
    x_bounds: torch.Tensor,
    y_bounds: torch.Tensor,
    start_xy: torch.Tensor,
    steps_adam: int = adam_steps,
    steps_lbfgs: int = lbfgs_steps,
    device="cpu",
):
    with torch.no_grad():
        sx0 = (start_xy[0] - x_bounds[0]) / (x_bounds[1] - x_bounds[0])
        sy0 = (start_xy[1] - y_bounds[0]) / (y_bounds[1] - y_bounds[0])
        u0 = torch.tensor([invert_sigmoid(sx0), invert_sigmoid(sy0)], dtype=torch.float32, device=device)

    u = torch.nn.Parameter(u0.clone().detach().requires_grad_(True))

    # Adam 粗调
    opt = torch.optim.Adam([u], lr=adam_lr)
    for _ in range(steps_adam):
        opt.zero_grad(set_to_none=True)
        x, y = param_to_xy(u, x_bounds, y_bounds)
        inp = torch.stack([x, y]).unsqueeze(0)
        E = model(inp).squeeze()
        E.backward()
        opt.step()

    # LBFGS 精调
    opt_lbfgs = torch.optim.LBFGS([u], lr=0.5, max_iter=steps_lbfgs, line_search_fn="strong_wolfe")
    def closure():
        opt_lbfgs.zero_grad(set_to_none=True)
        x, y = param_to_xy(u, x_bounds, y_bounds)
        E = model(torch.stack([x, y]).unsqueeze(0)).squeeze()
        E.backward()
        return E
    opt_lbfgs.step(closure)

    with torch.no_grad():
        x, y = param_to_xy(u, x_bounds, y_bounds)
        E = model(torch.stack([x, y]).unsqueeze(0)).squeeze().item()
    return float(E), float(x.item()), float(y.item())

def global_search_min(
    model: nn.Module,
    x_bounds: torch.Tensor,
    y_bounds: torch.Tensor,
    n_starts: int = seed_count,
    device="cpu",
):
    seeds = grid_seed_samples(n_starts, x_bounds, y_bounds, device)
    corners = torch.tensor([
        [x_bounds[0], y_bounds[0]],
        [x_bounds[0], y_bounds[1]],
        [x_bounds[1], y_bounds[0]],
        [x_bounds[1], y_bounds[1]],
    ], dtype=torch.float32, device=device)
    seeds = torch.cat([seeds, corners], dim=0)

    best = {"E": float("inf"), "x": None, "y": None}
    for i in range(seeds.shape[0]):
        E, x, y = refine_one_start(model, x_bounds, y_bounds, seeds[i], device=device)
        if E < best["E"]:
            best = {"E": E, "x": x, "y": y}
    return best

# ---------- 主程序 ----------
def main():
    device = "cpu"

    # === 固定搜索范围 ===
    # 你当前设置：
    x0, x1 = 0.5, 1.5
    y0, y1 = 0.5, 1.5
    # 如果要在 [0, 2] × [0, 2] 搜索，请改为：
    # x0, x1 = 0.0, 2.0
    # y0, y1 = 0.0, 2.0

    x_bounds = torch.tensor([x0, x1], dtype=torch.float32, device=device)
    y_bounds = torch.tensor([y0, y1], dtype=torch.float32, device=device)

    model = load_model(model_path).to(device)

    result = global_search_min(model, x_bounds, y_bounds, n_starts=seed_count, device=device)
    out = {
        "min_energy": result["E"],
        "x": result["x"],
        "y": result["y"],
        "x_bounds": [x0, x1],
        "y_bounds": [y0, y1],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
