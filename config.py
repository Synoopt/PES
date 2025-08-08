def get_config(config):
    base_config = {
        "input_dim": 2,
        "output_dim": 1,
        "train_data_path": "input_force_filtered.csv",
    }

    model_configs = {
        "2-64": {  # Name of this training
            "hidden_dim": 64,  # The dimension (number of neurons) of the hidden layer.
            "num_layers": 2,  # The number of hidden layers.
            "learning_rate": 0.001,  # The initial learning rate.
            "weight": 70,  # The weight of tthe gradient during the learning process.
            "activation_function": "Mish",  # The activation function.
            "save_model_path": "2-64.pth",  # The file path to save the model.
            "saveaxpath": "ax.png",  # The file path to save the 3D PES plot.
            "saveaxpath2": "ax2.png",  # The file path to save the 2D contour path.
            "assesspath": "assess.png",  # The file path to save the Actual-Predicted pic.
        },

    }

    # Return combined configuration
    specific_config = model_configs[config]
    configure = {**base_config, **specific_config}
    return configure
