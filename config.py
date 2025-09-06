"""
Configuration registry.

Configuration registry: centrally manage different model configurations and provide default training hyperparameters.
"""

DEFAULT_CONFIG_NAME = "2-64"  # Default config name / default config name


def list_config_names():
    """
    List available model config names.

    List available model configuration names.
    """
    return list(_MODEL_CONFIGS.keys())


def get_config(config_name):
    """
    Get merged configuration by name (base + specific).

    Get merged configuration by name (base items + specific items).
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

    Get all configurations and merge with base defaults.
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

