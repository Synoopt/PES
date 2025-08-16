"""
Configuration registry.

配置注册：集中管理不同模型配置，并提供默认训练超参。
"""

DEFAULT_CONFIG_NAME = "2-64"  # 默认配置名 / default config name


def list_config_names():
    """
    List available model config names.

    列出可用模型配置名。
    """
    return list(_MODEL_CONFIGS.keys())


def get_config(config_name):
    """
    Get merged configuration by name (base + specific).

    按名称获取合并后的配置（基础项 + 特定项）。
    """
    base_config = {
        "input_dim": 2,
        "output_dim": 1,
        "train_data_path": "input_force_filtered.csv",
        # Training hyperparameters (can be overridden via CLI)
        "epochs": 1000,
        "patience": 50,
        "min_delta": 1e-4,
        "scheduler_mode": "min",
        "scheduler_patience": 10,
        "scheduler_factor": 0.67,
    }

    specific_config = _MODEL_CONFIGS[config_name]
    return {**base_config, **specific_config}


def get_all_configs():
    """
    Get all configs expanded with base defaults.

    获取所有配置，并融合基础默认项。
    """
    base = get_config(DEFAULT_CONFIG_NAME)
    return {name: {**base, **cfg} for name, cfg in _MODEL_CONFIGS.items()}


_MODEL_CONFIGS = {
    "2-64": {
        "hidden_dim": 64,
        "num_layers": 2,
        "learning_rate": 0.001,
        "weight": 0.014,
        "activation_function": "Mish",
        "save_model_path": "2-64.pth",
        "saveaxpath": "ax.png",
        "saveaxpath2": "ax2.png",
        "assesspath": "assess.png",
    },
    "3-32": {
        "hidden_dim": 32,
        "num_layers": 3,
        "learning_rate": 0.001,
        "weight": 0.014,
        "activation_function": "Mish",
        "save_model_path": "3-32.pth",
        "saveaxpath": "ax.png",
        "saveaxpath2": "ax2.png",
        "assesspath": "assess.png",
    },
}

