## PES 项目使用说明 / PES Project Guide

如果你偏好单语阅读，请查看：
- 中文版：`README.zh-CN.md`
- English: `README.en.md`

If you prefer a bilingual quick guide, continue reading below.

---

### 功能概览 / Features

- 训练 Train: 使用 CSV 数据训练神经网络势能面
- 可视化 Visualize: 生成真实-预测散点、3D 曲面与 2D 等高线
- 分子模拟 Simulate: 使用已训练 PES 的梯度进行简易 MD 模拟
- 日志与指标 Logging: TensorBoard 指标可视化

---

### 环境准备 / Environment Setup

1) 建议使用虚拟环境 / Recommended virtual environment
```
python3 -m venv .venv
source .venv/bin/activate  # Windows 使用 .venv\Scripts\activate
```

2) 安装依赖 / Install dependencies
```
pip install -r requirements.txt
```

如需 GPU，请确保正确安装支持 CUDA 的 PyTorch 版本。For GPU support, install the proper CUDA-enabled PyTorch build.

---

### 快速开始 / Quickstart

命令行 CLI：
```
# 训练 / Train (Unix/macOS)
./run.sh train --config 2-64 --data input_force_filtered.csv --out 2-64
# 训练 / Train (Windows)
run.bat train --config 2-64 --data input_force_filtered.csv --out 2-64

# 可视化 / Visualize (Unix/macOS)
./run.sh visualize --config 2-64 --data input_force_filtered.csv --model-dir 2-64
# 可视化 / Visualize (Windows)
run.bat visualize --config 2-64 --data input_force_filtered.csv --model-dir 2-64

# 分子模拟 / Simulate (Unix/macOS)
./run.sh simulate --config 2-64 --model-dir 2-64 --steps 50000
# 分子模拟 / Simulate (Windows)
run.bat simulate --config 2-64 --model-dir 2-64 --steps 50000

# 列出配置 / List configs (Unix/macOS)
./run.sh list-configs
# 列出配置 / List configs (Windows)
run.bat list-configs
```

图形界面 GUI：
```
# Unix/macOS
./run.sh gui
# Windows
run.bat gui
# 浏览器访问 / Visit: http://localhost:8501
```

GUI 支持中英文切换：侧边栏顶部选择 Language/语言，即可实时切换文案。
The GUI supports language switching (Chinese/English). Use the language selector in the sidebar.

### 跨平台运行 / Cross-platform Execution

项目提供两个运行脚本：
- `run.sh`：适用于 Unix/Linux/macOS 系统
- `run.bat`：适用于 Windows 系统

Both scripts support the same commands and arguments.
两个脚本支持相同的命令和参数。

---

### 数据格式 / Data Format

训练 CSV 需包含以下列：`x`, `y`, `z1`, `z2`, `z3`, `z4`。
`x, y` 为输入坐标，`z1..z4` 为目标值（其中 `z1` 用于主任务，`z2..z4` 为目标梯度）。

The training CSV must have columns: `x`, `y`, `z1`, `z2`, `z3`, `z4`. `x, y` are inputs, `z1` is the main target, `z2..z4` are target gradients.

---

### 配置 / Configuration

查看 `config.py`。`DEFAULT_CONFIG_NAME` 指定默认配置。每个配置包含：
- `hidden_dim`, `num_layers`, `activation_function`
- `learning_rate`, `epochs`, `patience`, `min_delta`（逐样本训练，等效 batch size=1）
- `train_data_path`
- 可视化输出文件名（`saveaxpath`, `saveaxpath2`, `assesspath`）与模型保存名 `save_model_path`

使用 CLI/GUI 可覆盖多数参数。You can override most parameters via CLI/GUI.

---

### 代码结构 / Code Structure

- `main.py`: 命令行入口（train/visualize/simulate/list-configs）
- `gui.py`: Streamlit 图形界面
- `model.py`: 神经网络模型定义（按名称解析激活函数）
- `train.py`: 训练循环（提前停止、学习率调度、TensorBoard 日志）
- `data_loader.py`: CSV 数据加载为 PyTorch DataLoader
- `utils.py`: 可视化、评估、日志与工具函数
- `loss.py`: 自定义损失（值 MSE + 梯度 MSE）
- `molecular_simulation.py`: 基于势能梯度的简易分子动力学模拟
- `config.py`: 配置注册与默认超参
- `mkdir.py`: 目录创建小工具

---

### 训练 / Training

CLI 示例 / CLI example:
```
# Unix/macOS
./run.sh train --config 2-64 --data input_force_filtered.csv --out 2-64 \
  --epochs 800 --patience 60 --lr 0.0005 --activation ReLU
# Windows
run.bat train --config 2-64 --data input_force_filtered.csv --out 2-64 \
  --epochs 800 --patience 60 --lr 0.0005 --activation ReLU
```

训练过程中会在 `logs/` 下生成 TensorBoard 日志：
```
tensorboard --logdir logs
```

---

### 可视化 / Visualization

训练完成后将生成：
- 真实-预测一致性图 `assess.png`
- 3D PES 曲面 `ax.png`
- 2D 等高线 `ax2.png`

对应命令见上文。The command is shown above.

---

### 分子模拟 / Simulation

示例 / Example:
```
# Unix/macOS
./run.sh simulate --config 2-64 --model-dir 2-64 --steps 60000 --dt 1e-18 \
  --x1 3.0 --x2 0.0 --x3 -1.108 --v1 -20000 --v2 0 --v3 0
# Windows
run.bat simulate --config 2-64 --model-dir 2-64 --steps 60000 --dt 1e-18 \
  --x1 3.0 --x2 0.0 --x3 -1.108 --v1 -20000 --v2 0 --v3 0
```

输出包括：
- 轨迹 CSV `simulation_results.csv`
- XYZ 文件 `<config>_trajectory.xyz`
- MD 等高线与轨迹 `*_MD.png`
- 总能量曲线 `*_Energy.png`

---

### 常见问题 / FAQ

- CUDA 不可用？请安装支持 CUDA 的 PyTorch 或使用 CPU 模式。
- 可视化空白？确认数据列名与范围是否正确（x, y ∈ [0.5, 4.0]）。
- R2 很低？尝试增大网络宽度/层数、调整学习率或训练轮数。

---

### 许可证 / License

如无特殊声明，默认以本项目 LICENSE 条款为准。Unless specified otherwise, use this repo's LICENSE.


