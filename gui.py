"""
Streamlit-based GUI for PES workflows.

Simple graphical interface based on Streamlit: training, visualization and molecular simulation.
"""

import os
import io
import time
import re
from datetime import datetime
import pandas as pd
import streamlit as st
import torch
from config import get_config, list_config_names, DEFAULT_CONFIG_NAME
from model import NeuralNetwork
from data_loader import load_data
from train import train
from utils import visualize_model, accuracy, load_model, ensure_dir
from loss import CustomLoss
from torch.optim.lr_scheduler import ReduceLROnPlateau
from molecular_simulation import run_simulation

st.set_page_config(page_title="PES GUI", layout="wide")

# i18n dictionary / Internationalization dictionary
TEXT = {
    "zh": {
        "title": "PES 用户界面",
        "sidebar_settings": "全局设置",
        "choose_config": "选择配置",
        "language": "语言 / Language",
        "lang_zh": "中文",
        "lang_en": "English",
        "device_on": "CUDA 可用",
        "device_off": "CUDA 不可用（使用 CPU）",
        "atom_config": "原子配置",
        "atom1_label": "第一个原子",
        "atom2_label": "第二个原子",
        "atom3_label": "第三个原子",
        "atom_help": "设置三个原子的类型，用于图表标签和文件名",
        "tab_train": "训练",
        "tab_vis": "可视化",
        "tab_sim": "分子模拟",
        "train_model": "训练模型",
        "dataset": "数据集",
        "upload_train": "上传训练 CSV (包含列 x, y, z1..z4)",
        "input_train_path": "或指定训练数据路径",
        "start_train": "开始训练",
        "loading_data": "加载数据中...",
        "training": "训练中，请稍候...（可在 logs/ 下用 TensorBoard 查看进度）",
        "train_done": "训练完成，R2 = {r2}",
        "train_fail": "训练失败: {err}",
        "cap_fit": "真实-预测一致性",
        "cap_3d": "3D 等高线",
        "cap_2d": "2D 等高线",
        "visualize": "可视化已训练模型",
        "upload_vis": "上传用于可视化的 CSV",
        "input_data_path": "或指定数据路径",
        "gen_plots": "生成可视化图像",
        "vis_done": "可视化完成，R2 = {r2}",
        "vis_fail": "可视化失败: {err}",
        "simulate": "分子动力学模拟",
        "steps": "步数",
        "dt": "时间步长",
        "start_sim": "开始模拟",
        "sim_running": "运行模拟中...",
        "sim_done": "模拟完成",
        "cap_md": "MD 等高线轨迹",
        "cap_energy": "总能量曲线",
        "exports": "导出:",
        "sim_fail": "模拟失败: {err}",
        "epochs": "训练轮数",

        "hidden_dim": "隐藏层维度",
        "patience": "耐心值",
        "learning_rate": "学习率",
        "num_layers": "隐藏层数量",
        "min_delta": "最小改进",
        "gradient_weight": "梯度权重",
        "activation": "激活函数",

        "auto_model_dir": "已自动选择模型目录：{d}",
        "auto_model_file": "已自动选择模型文件：{f}",
        "no_model_found": "未找到任何已训练的模型文件（.pth）。请先在'训练'页训练一个模型。",
        "adv_settings": "高级设置（可选）",
        "override_model_dir": "手动覆盖模型目录",
        "override_model_file": "手动覆盖模型文件名（目录下）",
    },
    "en": {
        "title": "PES GUI",
        "sidebar_settings": "Global Settings",
        "choose_config": "Choose Config",
        "language": "Language / 语言",
        "lang_zh": "中文",
        "lang_en": "English",
        "device_on": "CUDA available",
        "device_off": "CUDA unavailable (CPU)",
        "atom_config": "Atom Configuration",
        "atom1_label": "First Atom",
        "atom2_label": "Second Atom",
        "atom3_label": "Third Atom",
        "atom_help": "Set the types of three atoms for chart labels and filenames",
        "tab_train": "Train",
        "tab_vis": "Visualize",
        "tab_sim": "Simulate",
        "train_model": "Train Model",
        "dataset": "Dataset",
        "upload_train": "Upload training CSV (columns: x, y, z1..z4)",
        "input_train_path": "Or specify training data path",
        "start_train": "Start Training",
        "loading_data": "Loading data...",
        "training": "Training... (Use TensorBoard under logs/)",
        "train_done": "Training done, R2 = {r2}",
        "train_fail": "Training failed: {err}",
        "cap_fit": "True vs Predict",
        "cap_3d": "3D PES",
        "cap_2d": "2D Contour",
        "visualize": "Visualize Trained Model",
        "upload_vis": "Upload CSV for visualization",
        "input_data_path": "Or specify data path",
        "gen_plots": "Generate Plots",
        "vis_done": "Visualization done, R2 = {r2}",
        "vis_fail": "Visualization failed: {err}",
        "simulate": "Molecular Dynamics Simulation",
        "steps": "steps",
        "dt": "dt",
        "start_sim": "Start Simulation",
        "sim_running": "Running simulation...",
        "sim_done": "Simulation finished",
        "cap_md": "MD Contour Path",
        "cap_energy": "Total Energy",
        "exports": "Outputs:",
        "sim_fail": "Simulation failed: {err}",
        "epochs": "epochs",

        "hidden_dim": "hidden_dim",
        "patience": "patience",
        "learning_rate": "learning_rate",
        "num_layers": "num_layers",
        "min_delta": "min_delta",
        "gradient_weight": "gradient_weight",
        "activation": "activation",

        "auto_model_dir": "Auto-selected model dir: {d}",
        "auto_model_file": "Auto-selected model file: {f}",
        "no_model_found": "No trained model (.pth) found. Please train one first on the Train tab.",
        "adv_settings": "Advanced (optional)",
        "override_model_dir": "Override model directory",
        "override_model_file": "Override model filename (in directory)",
    },
}

def t(lang_code: str, key: str) -> str:
    return TEXT.get(lang_code, TEXT["zh"]).get(key, key)

# -------- Utilities for auto-detecting latest model --------
ACTIVATIONS = {"Mish", "ReLU", "LeakyReLU", "ELU", "GELU"}
STEM_REGEX = re.compile(r"^(\d+)-(\d+)-([A-Za-z]+)$")
TS_SUFFIX = re.compile(r"-\d{8}-\d{6}$")  # -YYYYMMDD-HHMMSS

# Initialize session state for atom configuration
if 'atom1_type' not in st.session_state:
    st.session_state.atom1_type = "H"
if 'atom2_type' not in st.session_state:
    st.session_state.atom2_type = "H"
if 'atom3_type' not in st.session_state:
    st.session_state.atom3_type = "Ne"

def list_pth_files(dirpath: str):
    try:
        return [
            os.path.join(dirpath, f)
            for f in os.listdir(dirpath)
            if f.endswith(".pth") and os.path.isfile(os.path.join(dirpath, f))
        ]
    except Exception:
        return []

def latest_pth_in_dir(dirpath: str):
    pths = list_pth_files(dirpath)
    if not pths:
        return None
    pths.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return pths[0]

def find_latest_model_dir(base_dir: str = "."):
    """Pick the directory whose newest .pth is the freshest overall."""
    candidates = []
    try:
        for name in os.listdir(base_dir):
            d = os.path.join(base_dir, name)
            if not os.path.isdir(d):
                continue
            p = latest_pth_in_dir(d)
            if p:
                candidates.append((os.path.getmtime(p), d))
    except Exception:
        pass
    if not candidates:
        return None
    candidates.sort(reverse=True, key=lambda x: x[0])
    return candidates[0][1]

def parse_stem_to_arch(stem: str):
    """
    stem format: "<num_layers>-<hidden_dim>-<activation>"
    """
    m = STEM_REGEX.match(stem)
    if not m:
        return None
    num_layers = int(m.group(1))
    hidden_dim = int(m.group(2))
    act = m.group(3)
    if act not in ACTIVATIONS:
        return None
    return {"num_layers": num_layers, "hidden_dim": hidden_dim, "activation_function": act}

def save_uploaded_to(path: str, uploaded_file) -> str:
    """
    Save an uploaded file to disk.

    Save uploaded file to disk.
    """
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

def ensure_latest_alias(model_dir: str, cfg_default_model_name: str, latest_model_path: str):
    """
    Some downstream funcs (e.g., run_simulation) may expect cfg['save_model_path'] under model_dir.
    To satisfy that without changing their code, copy/symlink the latest model to that expected name.
    """
    try:
        ensure_dir(model_dir)
        alias_path = os.path.join(model_dir, cfg_default_model_name)
        # Prefer symlink if possible; fall back to copy if symlink fails.
        if os.path.islink(alias_path) or os.path.exists(alias_path):
            try:
                os.remove(alias_path)
            except Exception:
                pass
        try:
            os.symlink(os.path.abspath(latest_model_path), alias_path)
        except Exception:
            # Copy fallback
            import shutil
            shutil.copy2(latest_model_path, alias_path)
        return alias_path
    except Exception:
        return None

with st.sidebar:
    # language selection / Language selection
    lang_label = t("zh", "language")  # label itself bilingual
    lang_display = st.selectbox(lang_label, [t( "zh", "lang_zh"), t("zh", "lang_en")], index=0)
    lang_code = "zh" if lang_display == t("zh", "lang_zh") else "en"

    st.header(t(lang_code, "sidebar_settings"))
    selected_config = st.selectbox(
        t(lang_code, "choose_config"),
        list_config_names(),
        index=list_config_names().index(DEFAULT_CONFIG_NAME),
    )
    device_info = t(lang_code, "device_on") if torch.cuda.is_available() else t(lang_code, "device_off")
    st.caption(device_info)

    st.subheader(t(lang_code, "atom_config"))
    atom1_type = st.selectbox(t(lang_code, "atom1_label"), 
                              ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca"], 
                              index=["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca"].index(st.session_state.atom1_type),
                              key="atom1_select")
    atom2_type = st.selectbox(t(lang_code, "atom2_label"), 
                              ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca"], 
                              index=["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca"].index(st.session_state.atom2_type),
                              key="atom2_select")
    atom3_type = st.selectbox(t(lang_code, "atom3_label"), 
                              ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca"], 
                              index=["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca"].index(st.session_state.atom3_type),
                              key="atom3_select")
    
    # Update session state when selection changes
    st.session_state.atom1_type = atom1_type
    st.session_state.atom2_type = atom2_type
    st.session_state.atom3_type = atom3_type
    
    # Display current configuration summary
    if lang_code == "zh":
        st.info(f"当前配置: {atom1_type}-{atom2_type}-{atom3_type} 系统")
    else:
        st.info(f"Current Configuration: {atom1_type}-{atom2_type}-{atom3_type} System")
    
    st.caption(t(lang_code, "atom_help"))

st.title(t(lang_code, "title"))

TAB_TRAIN, TAB_VIS, TAB_SIM = st.tabs([t(lang_code, "tab_train"), t(lang_code, "tab_vis"), t(lang_code, "tab_sim")])


# =========================
# TAB 1: TRAIN
# =========================
with TAB_TRAIN:
    st.subheader(t(lang_code, "train_model"))

    cfg = get_config(selected_config)

    col1, col2, col3 = st.columns(3)
    with col1:
        epochs = st.number_input(t(lang_code, "epochs"), min_value=1, value=int(cfg["epochs"]))
        hidden_dim = st.number_input(t(lang_code, "hidden_dim"), min_value=1, value=int(cfg["hidden_dim"]))
    with col2:
        patience = st.number_input(t(lang_code, "patience"), min_value=1, value=int(cfg["patience"]))
        lr = st.number_input(t(lang_code, "learning_rate"), min_value=1e-6, format="%f", value=float(cfg["learning_rate"]))
        num_layers = st.number_input(t(lang_code, "num_layers"), min_value=1, value=int(cfg["num_layers"]))
    with col3:
        min_delta = st.number_input(t(lang_code, "min_delta"), min_value=0.0, format="%f", value=float(cfg["min_delta"]))
        weight = st.number_input(t(lang_code, "gradient_weight"), min_value=0.0, format="%f", value=float(cfg["weight"]))
        activation = st.selectbox(t(lang_code, "activation"), ["Mish", "ReLU", "LeakyReLU", "ELU", "GELU"], index=0)

    st.markdown("---")

    st.write(t(lang_code, "dataset"))
    uploaded_train = st.file_uploader(t(lang_code, "upload_train"), type=["csv"], key="train_csv")
    default_data_path = cfg["train_data_path"]
    data_path_text = st.text_input(t(lang_code, "input_train_path"), value=default_data_path)

    if st.button(t(lang_code, "start_train"), type="primary"):
        try:
            # Update configuration (using values from input boxes)
            cfg["epochs"], cfg["patience"], cfg["min_delta"] = int(epochs), int(patience), float(min_delta)
            cfg["learning_rate"], cfg["weight"] = float(lr), float(weight)
            cfg["hidden_dim"], cfg["num_layers"], cfg["activation_function"] = int(hidden_dim), int(num_layers), activation

            # Automatically generate directory name (with timestamp) and filename (also with timestamp)
            stem = f"{cfg['num_layers']}-{cfg['hidden_dim']}-{cfg['activation_function']}"
            tag = datetime.now().strftime("%Y%m%d-%H%M%S")
            out_dir = f"{stem}-{tag}"         # Directory also has timestamp
            ensure_dir(out_dir)

            cfg["save_model_path"] = f"{stem}-{tag}.pth"   # Filename matches directory name
            cfg["saveaxpath"] = f"{stem}-3d.png"
            cfg["saveaxpath2"] = f"{stem}-2d.png"
            cfg["assesspath"] = f"{stem}-fit.png"

            # Training data path
            if uploaded_train is not None:
                data_path = os.path.join(out_dir, "uploaded_train.csv")
                save_uploaded_to(data_path, uploaded_train)
            else:
                data_path = data_path_text

            save_model_path = f"{out_dir}/{cfg['save_model_path']}"
            savepath = f"{out_dir}/{cfg['saveaxpath']}"
            savepath2 = f"{out_dir}/{cfg['saveaxpath2']}"
            saverocpath = f"{out_dir}/{cfg['assesspath']}"

            # Data loading
            with st.spinner(t(lang_code, "loading_data")):
                train_loader, data = load_data(data_path)

            # Build model
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model = NeuralNetwork(
                cfg['input_dim'],
                cfg['hidden_dim'],
                cfg['num_layers'],
                cfg['output_dim'],
                cfg['activation_function']
            ).to(device)

            # Optimizer and scheduler
            criterion = CustomLoss()
            optimizer = torch.optim.Adam(model.parameters(), lr=cfg['learning_rate'])
            scheduler = ReduceLROnPlateau(
                optimizer,
                cfg['scheduler_mode'],
                patience=cfg['scheduler_patience'],
                factor=cfg['scheduler_factor']
            )

            # Training
            with st.spinner(t(lang_code, "training")):
                train(
                    model,
                    train_loader,
                    criterion,
                    optimizer,
                    scheduler,
                    save_model_path,
                    data,
                    cfg['weight'],
                    selected_config,
                    epochs=cfg['epochs'],
                    patience=cfg['patience'],
                    min_delta=cfg['min_delta'],
                )

            # Evaluation and visualization
            model = load_model(model, save_model_path)
            visualize_model(model, data, savepath, savepath2, saverocpath, atom1_type, atom2_type, atom3_type)
            r2 = accuracy(model, data)
            st.success(t(lang_code, "train_done").format(r2=f"{r2:.6f}"))
            st.image([saverocpath, savepath, savepath2],
                     caption=[t(lang_code, "cap_fit"), t(lang_code, "cap_3d"), t(lang_code, "cap_2d")],
                     use_container_width=True)
        except Exception as e:
            st.error(t(lang_code, "train_fail").format(err=e))


# =========================
# TAB 2: VISUALIZE
# =========================
with TAB_VIS:
    st.subheader(t(lang_code, "visualize"))

    cfg = get_config(selected_config)

    # ---- Auto-pick latest model dir & .pth ----
    auto_dir = find_latest_model_dir(".")
    auto_model_path = latest_pth_in_dir(auto_dir) if auto_dir else None

    if not auto_dir or not auto_model_path:
        st.warning(t(lang_code, "no_model_found"))
    else:
        st.caption(t(lang_code, "auto_model_dir").format(d=auto_dir))
        st.caption(t(lang_code, "auto_model_file").format(f=os.path.basename(auto_model_path)))

    # Optional override area
    with st.expander(t(lang_code, "adv_settings")):
        override_dir = st.text_input(t(lang_code, "override_model_dir"), value=auto_dir or "", key="vis_override_dir")
        if override_dir.strip():
            auto_dir = override_dir.strip()
            auto_model_path = latest_pth_in_dir(auto_dir)
        override_file = st.text_input(t(lang_code, "override_model_file"),
                                      value=os.path.basename(auto_model_path) if auto_model_path else "",
                                      key="vis_override_file")
        if override_file.strip():
            auto_model_path = os.path.join(auto_dir, override_file.strip()) if auto_dir else None

    # data input
    uploaded_vis = st.file_uploader(t(lang_code, "upload_vis"), type=["csv"], key="vis_csv")
    data_path_text = st.text_input(t(lang_code, "input_data_path"),
                                   value=cfg["train_data_path"], key="vis_path")

    if st.button(t(lang_code, "gen_plots")):
        try:
            if not auto_dir or not auto_model_path or not os.path.exists(auto_model_path):
                st.error(t(lang_code, "no_model_found"))
            else:
                # Parse structure parameters from directory name: first remove timestamp suffix then parse
                dir_base = os.path.basename(auto_dir)
                stem_no_ts = TS_SUFFIX.sub("", dir_base)
                arch = parse_stem_to_arch(stem_no_ts)
                if arch:
                    cfg["num_layers"] = arch["num_layers"]
                    cfg["hidden_dim"] = arch["hidden_dim"]
                    cfg["activation_function"] = arch["activation_function"]

                # Data preparation
                if uploaded_vis is not None:
                    data_path = os.path.join(auto_dir, "uploaded_visualize.csv")
                    save_uploaded_to(data_path, uploaded_vis)
                else:
                    data_path = data_path_text

                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                model = NeuralNetwork(
                    cfg['input_dim'],
                    cfg['hidden_dim'],
                    cfg['num_layers'],
                    cfg['output_dim'],
                    cfg['activation_function']
                ).to(device)

                # Directly use auto-selected .pth
                model = load_model(model, auto_model_path)

                _, data = load_data(data_path)

                # Output image paths (overwrite/update visualization plots in this directory)
                cfg["saveaxpath"] = f"{stem_no_ts}-3d.png"
                cfg["saveaxpath2"] = f"{stem_no_ts}-2d.png"
                cfg["assesspath"] = f"{stem_no_ts}-fit.png"
                savepath = os.path.join(auto_dir, cfg["saveaxpath"])
                savepath2 = os.path.join(auto_dir, cfg["saveaxpath2"])
                saverocpath = os.path.join(auto_dir, cfg["assesspath"])

                visualize_model(model, data, savepath, savepath2, saverocpath, atom1_type, atom2_type, atom3_type)
                r2 = accuracy(model, data)
                st.success(t(lang_code, "vis_done").format(r2=f"{r2:.6f}"))
                st.image([saverocpath, savepath, savepath2],
                         caption=[t(lang_code, "cap_fit"), t(lang_code, "cap_3d"), t(lang_code, "cap_2d")],
                         use_container_width=True)
        except Exception as e:
            st.error(t(lang_code, "vis_fail").format(err=e))


# =========================
# TAB 3: SIMULATE (MD)
# =========================
with TAB_SIM:
    st.subheader(t(lang_code, "simulate"))

    cfg = get_config(selected_config)

    # ---- Auto-pick latest model dir & .pth ----
    auto_dir = find_latest_model_dir(".")
    auto_model_path = latest_pth_in_dir(auto_dir) if auto_dir else None

    if not auto_dir or not auto_model_path:
        st.warning(t(lang_code, "no_model_found"))
    else:
        st.caption(t(lang_code, "auto_model_dir").format(d=auto_dir))
        st.caption(t(lang_code, "auto_model_file").format(f=os.path.basename(auto_model_path)))

    with st.expander(t(lang_code, "adv_settings")):
        override_dir = st.text_input(t(lang_code, "override_model_dir"), value=auto_dir or "", key="sim_override_dir")
        if override_dir.strip():
            auto_dir = override_dir.strip()
            auto_model_path = latest_pth_in_dir(auto_dir)
        override_file = st.text_input(t(lang_code, "override_model_file"),
                                      value=os.path.basename(auto_model_path) if auto_model_path else "",
                                      key="sim_override_file")
        if override_file.strip():
            auto_model_path = os.path.join(auto_dir, override_file.strip()) if auto_dir else None

    steps = st.number_input(t(lang_code, "steps"), min_value=1, value=60000)
    dt = st.number_input(t(lang_code, "dt"), min_value=1e-22, value=10e-19, format="%e")

    c1, c2, c3 = st.columns(3)
    with c1:
        x1 = st.number_input("x1", value=3.0)
        v1 = st.number_input("v1", value=-20000.0)
    with c2:
        x2 = st.number_input("x2", value=0.0)
        v2 = st.number_input("v2", value=0.0)
    with c3:
        x3 = st.number_input("x3", value=-1.108)
        v3 = st.number_input("v3", value=0.0)

    if st.button(t(lang_code, "start_sim")):
        try:
            if not auto_dir or not auto_model_path or not os.path.exists(auto_model_path):
                st.error(t(lang_code, "no_model_found"))
            else:
                with st.spinner(t(lang_code, "sim_running")):
                    # Compatible with run_simulation possibly using cfg['save_model_path']:
                    default_model_name = get_config(selected_config).get("save_model_path", "model.pth")
                    alias_path = ensure_latest_alias(auto_dir, default_model_name, auto_model_path)

                    # Parse directory name to get structure (remove timestamp)
                    dir_base = os.path.basename(auto_dir)
                    stem_no_ts = TS_SUFFIX.sub("", dir_base)
                    arch = parse_stem_to_arch(stem_no_ts)
                    if arch:
                        cfg["num_layers"] = arch["num_layers"]
                        cfg["hidden_dim"] = arch["hidden_dim"]
                        cfg["activation_function"] = arch["activation_function"]

                    outputs = run_simulation(
                        config_name=selected_config,
                        model_dir=auto_dir,  # Use auto-selected directory
                        steps=int(steps),
                        dt=float(dt),
                        init_x1=float(x1),
                        init_x2=float(x2),
                        init_x3=float(x3),
                        init_v1=float(v1),
                        init_v2=float(v2),
                        init_v3=float(v3),
                    )
                st.success(t(lang_code, "sim_done"))
                st.image([outputs["md_plot"], outputs["energy_plot"]],
                         caption=[t(lang_code, "cap_md"), t(lang_code, "cap_energy")],
                         use_container_width=True)
                st.write(t(lang_code, "exports"))
                st.write(outputs)
        except Exception as e:
            st.error(t(lang_code, "sim_fail").format(err=e))
