"""
Command-line entrypoint for PES project.

Command line entry: provides four subcommands: train / visualize / simulate / list-configs,
used for training models, visualization and molecular dynamics simulation.
"""
import os
import argparse
from mkdir import create_folders
from data_loader import load_data
from model import NeuralNetwork
from loss import CustomLoss
from config import get_config, list_config_names, DEFAULT_CONFIG_NAME
from train import train
from utils import visualize_model, accuracy, load_model, ensure_dir
import numpy as np
import pandas as pd
import torch
from torch.optim.lr_scheduler import ReduceLROnPlateau
from molecular_simulation import run_simulation


def cli():
    """
    Parse arguments and dispatch subcommands.

    Parse command line arguments and dispatch to corresponding subcommands.
    """
    parser = argparse.ArgumentParser(description="PES Project Command Line Tool / PES CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # train command
    p_train = subparsers.add_parser("train", help="Train model")
    p_train.add_argument("--config", default=DEFAULT_CONFIG_NAME, choices=list_config_names())
    p_train.add_argument("--data", default=None, help="Training data CSV path, default reads from config")
    p_train.add_argument("--out", default=None, help="Output directory (default uses config name)")
    p_train.add_argument("--epochs", type=int, default=None)
    p_train.add_argument("--patience", type=int, default=None)
    p_train.add_argument("--lr", type=float, default=None)
    p_train.add_argument("--weight", type=float, default=None)
    p_train.add_argument("--hidden-dim", type=int, default=None)
    p_train.add_argument("--num-layers", type=int, default=None)
    p_train.add_argument("--activation", type=str, default=None)

    # visualize command
    p_vis = subparsers.add_parser("visualize", help="Load trained model and visualize")
    p_vis.add_argument("--config", default=DEFAULT_CONFIG_NAME, choices=list_config_names())
    p_vis.add_argument("--data", required=True, help="Data CSV path")
    p_vis.add_argument("--model-dir", required=True, help="Model directory (contains saved weights)")

    # simulate command
    p_sim = subparsers.add_parser("simulate", help="Run molecular dynamics simulation")
    p_sim.add_argument("--config", default=DEFAULT_CONFIG_NAME, choices=list_config_names())
    p_sim.add_argument("--model-dir", required=True, help="Model directory (contains saved weights)")
    p_sim.add_argument("--steps", type=int, default=60000)
    p_sim.add_argument("--dt", type=float, default=10e-19)
    p_sim.add_argument("--x1", type=float, default=3.0)
    p_sim.add_argument("--x2", type=float, default=0.0)
    p_sim.add_argument("--x3", type=float, default=-1.108)
    p_sim.add_argument("--v1", type=float, default=-20000)
    p_sim.add_argument("--v2", type=float, default=0.0)
    p_sim.add_argument("--v3", type=float, default=0.0)

    # list-configs command
    subparsers.add_parser("list-configs", help="List available configuration names")

    args = parser.parse_args()

    if args.command == "list-configs":
        print("Available configurations:", ", ".join(list_config_names()))
        return

    if args.command == "train":
        # Train a model with optional overrides.
        # Train model: supports overriding default hyperparameters via command line.
        if torch.cuda.is_available():
            torch.cuda.init()
        cfg = get_config(args.config)
        # allow overrides
        if args.hidden_dim is not None:
            cfg["hidden_dim"] = args.hidden_dim
        if args.num_layers is not None:
            cfg["num_layers"] = args.num_layers
        if args.activation is not None:
            cfg["activation_function"] = args.activation
        if args.lr is not None:
            cfg["learning_rate"] = args.lr
        if args.weight is not None:
            cfg["weight"] = args.weight
        if args.epochs is not None:
            cfg["epochs"] = args.epochs
        if args.patience is not None:
            cfg["patience"] = args.patience

        train_data_path = args.data or cfg['train_data_path']
        out_dir = args.out or args.config
        ensure_dir(out_dir)
        save_model_path = f"{out_dir}/{cfg['save_model_path']}"
        savepath = f"{out_dir}/{cfg['saveaxpath']}"
        savepath2 = f"{out_dir}/{cfg['saveaxpath2']}"
        saverocpath = f"{out_dir}/{cfg['assesspath']}"

        # Data
        # Data loading
        train_loader, data = load_data(train_data_path)

        # Model
        # Build model
        model = NeuralNetwork(
            cfg['input_dim'], cfg['hidden_dim'], cfg['num_layers'], cfg['output_dim'], cfg['activation_function']
        )
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)

        # Optimization
        # Optimizer and learning rate scheduler
        criterion = CustomLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=cfg['learning_rate'])
        scheduler = ReduceLROnPlateau(
            optimizer, cfg['scheduler_mode'], patience=cfg['scheduler_patience'], factor=cfg['scheduler_factor']
        )

        run_name = cfg['save_model_path'].replace(".pth", "")
        # train
        train(
            model,
            train_loader,
            criterion,
            optimizer,
            scheduler,
            save_model_path,
            data,
            cfg['weight'],
            trainname = run_name,
            epochs=cfg['epochs'],
            patience=cfg['patience'],
            min_delta=cfg['min_delta'],
        )

        # Evaluation & Visualization
        # Evaluation and visualization
        model = load_model(model, save_model_path)
        visualize_model(model, data, savepath, savepath2, saverocpath)
        r2 = accuracy(model, data)
        print(f"R2: {r2:.6f}")
        # write to a CSV summary
        # Write results summary
        pd.DataFrame([[args.config, r2]], columns=["config", "r2"]).to_csv(f"{out_dir}/summary.csv", index=False)
        return

    if args.command == "visualize":
        # Load a trained model and generate plots.
        # Load trained model and generate plots.
        cfg = get_config(args.config)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = NeuralNetwork(
            cfg['input_dim'], cfg['hidden_dim'], cfg['num_layers'], cfg['output_dim'], cfg['activation_function']
        ).to(device)
        model_path = f"{args.model_dir}/{cfg['save_model_path']}"
        model = load_model(model, model_path)
        _, data = load_data(args.data)
        savepath = f"{args.model_dir}/{cfg['saveaxpath']}"
        savepath2 = f"{args.model_dir}/{cfg['saveaxpath2']}"
        saverocpath = f"{args.model_dir}/{cfg['assesspath']}"
        visualize_model(model, data, savepath, savepath2, saverocpath)
        r2 = accuracy(model, data)
        print(f"R2: {r2:.6f}")
        return

    if args.command == "simulate":
        # Run molecular dynamics simulation driven by the trained PES.
        # Run molecular dynamics simulation driven by the trained PES.
        run_simulation(
            config_name=args.config,
            model_dir=args.model_dir,
            steps=args.steps,
            dt=args.dt,
            init_x1=args.x1,
            init_x2=args.x2,
            init_x3=args.x3,
            init_v1=args.v1,
            init_v2=args.v2,
            init_v3=args.v3,
        )
        return


if __name__ == '__main__':
    cli()
