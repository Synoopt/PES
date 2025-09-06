## PES 项目使用说明（中文）

本仓库提供基于神经网络的势能面（PES）建模与分子动力学（MD）模拟，支持命令行（CLI）与简易图形界面（GUI）。

### 功能概览

- **训练**：使用 CSV 数据训练神经网络势能面
- **可视化**：生成真实-预测一致性散点、3D 曲面与 2D 等高线
- **分子模拟**：使用已训练的 PES 梯度驱动简易 MD 模拟
- **日志**：TensorBoard 指标可视化
- **原子配置**：自定义三原子系统，自动生成图表标签

### 环境准备

1) 建议使用虚拟环境
```
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2) 安装依赖
```
pip install -r requirements.txt
```

如需 GPU，请安装支持 CUDA 的 PyTorch 版本。

### 快速开始

CLI：
```
# 训练 (Unix/macOS)
./run.sh train --config 2-64 --data input_force_filtered.csv --out 2-64
# 训练 (Windows)
run.bat train --config 2-64 --data input_force_filtered.csv --out 2-64

# 可视化 (Unix/macOS)
./run.sh visualize --config 2-64 --data input_force_filtered.csv --model-dir 2-64
# 可视化 (Windows)
run.bat visualize --config 2-64 --data input_force_filtered.csv --model-dir 2-64

# 分子模拟 (Unix/macOS)
./run.sh simulate --config 2-64 --model-dir 2-64 --steps 50000
# 分子模拟 (Windows)
run.bat simulate --config 2-64 --model-dir 2-64 --steps 50000

# 列出可用配置 (Unix/macOS)
./run.sh list-configs
# 列出可用配置 (Windows)
run.bat list-configs
```

GUI：
```
# Unix/macOS
./run.sh gui
# Windows
run.bat gui
# 浏览器访问: http://localhost:8501
```

GUI 支持中英文切换：在侧边栏顶部选择 Language/语言 即可实时切换界面文案。

**原子配置功能**：在侧边栏"全局设置"部分，您可以配置三原子分子系统：
- **第一个原子**：从20种常见元素中选择 (H, He, Li, Be, B, C, N, O, F, Ne, Na, Mg, Al, Si, P, S, Cl, Ar, K, Ca)
- **第二个原子**：选择第二个原子类型
- **第三个原子**：选择第三个原子类型

选择的原子类型会自动应用到：
- 图表轴标签 (例如：X轴: Ne-H (Å), Y轴: H-H (Å))
- 图表标题 (例如："H-H-Ne 势能面")
- 所有生成的可视化图表

### 数据格式

训练 CSV 需包含列：`x`, `y`, `z1`, `z2`, `z3`, `z4`
- `x, y` 作为模型输入
- `z1` 作为主要回归目标
- `z2..z4` 为目标梯度（用于梯度监督损失）

### 配置

查看 `config.py`，`DEFAULT_CONFIG_NAME` 为默认配置。配置项包括：
- 模型：`hidden_dim`, `num_layers`, `activation_function`
- 训练：`learning_rate`, `epochs`, `patience`, `min_delta`（逐样本训练，等效 batch size=1）
- 数据：`train_data_path`
- 输出文件名：`save_model_path`, `saveaxpath`, `saveaxpath2`, `assesspath`

通过 CLI/GUI 可覆盖大部分参数。训练为逐样本，不再提供 `batch_size` 参数。

### 代码结构

- `main.py`：命令行入口（train/visualize/simulate/list-configs）
- `gui.py`：Streamlit 图形界面（支持中英切换和原子配置系统）
- `model.py`：神经网络模型（按名称解析激活函数）
- `train.py`：训练循环（提前停止、学习率调度、TensorBoard）
- `data_loader.py`：CSV 数据加载到 DataLoader
- `utils.py`：模型 I/O、日志、可视化、指标（支持原子感知标签）
- `loss.py`：值 MSE + 梯度 MSE 的加权损失
- `molecular_simulation.py`：基于势能面梯度的简易 MD 模拟
- `config.py`：配置注册与默认超参
- `mkdir.py`：批量创建目录工具

### 训练

示例：
```
# Unix/macOS
./run.sh train --config 2-64 --data input_force_filtered.csv --out 2-64 \
  --epochs 800 --patience 60 --lr 0.0005 --activation ReLU
# Windows
run.bat train --config 2-64 --data input_force_filtered.csv --out 2-64 \
  --epochs 800 --patience 60 --lr 0.0005 --activation ReLU
```

训练日志（TensorBoard）：
```
tensorboard --logdir logs
```

### 可视化

训练完成后会生成以下文件：
- 真实-预测一致性图：`assess.png`
- 3D PES 曲面：`ax.png`
- 2D 等高线：`ax2.png`

**原子配置集成**：使用GUI时，所有图表自动使用配置的原子类型：
- **3D 曲面图**：X轴 = {atom3}-{atom2} (Å), Y轴 = {atom2}-{atom1} (Å)
- **2D 等高线图**：标题显示 {atom1}-{atom2}-{atom3} 势能面
- **轴标签**：基于原子类型自动生成 (例如：Ne-H, H-H)

查看上方命令了解使用方法。

### 分子模拟

示例：
```
# Unix/macOS
./run.sh simulate --config 2-64 --model-dir 2-64 --steps 60000 --dt 1e-18 \
  --x1 3.0 --x2 0.0 --x3 -1.108 --v1 -20000 --v2 0 --v3 0
# Windows
run.bat simulate --config 2-64 --model-dir 2-64 --steps 60000 --dt 1e-18 \
  --x1 3.0 --x2 0.0 --x3 -1.108 --v1 -20000 --v2 0 --v3 0
```

输出：
- 轨迹 CSV：`simulation_results.csv`
- XYZ：`<config>_trajectory.xyz`
- 等高线与轨迹：`*_MD.png`
- 总能量曲线：`*_Energy.png`

### 注意事项

- 如果选择 `LeakyReLU` 作为激活函数，模型使用 `negative_slope=0.01`。
- Streamlit 图像渲染使用 `use_container_width=True`。
- 训练采用逐样本方式进行，以便更好地进行梯度监督。

### 常见问题（FAQ）

- CUDA 不可用？安装支持 CUDA 的 PyTorch 或使用 CPU。
- 图像空白？检查数据列名与范围（x,y ∈ [0.5, 4.0]）。
- R2 低？尝试增大网络规模、调整学习率与训练轮数。

### 许可证

遵循本仓库 LICENSE 条款。


