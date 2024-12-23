from mkdir import create_folders
from data_loader import load_data
from model import NeuralNetwork
from loss import CustomLoss
from config import get_config
from train import train, save_model
from utils import visualize_model, accuracy, load_model
import numpy as np
import pandas as pd
import torch
from torch.optim.lr_scheduler import ReduceLROnPlateau


def main():
    if torch.cuda.is_available():
        torch.cuda.init()
    config0 = ['2-64']  # change the name to the same as in config.py
    r = np.zeros(1)
    create_folders(config0)
    for con in config0:
        # load the config
        config1 = get_config(con)
        # convert the config into parameters
        input_dim = config1['input_dim']
        output_dim = config1['output_dim']
        hidden_dim = config1['hidden_dim']
        num_layers = config1['num_layers']
        weight = config1['weight']
        activation_function = "nn." + config1['activation_function'] + "()"
        lr = config1['learning_rate']
        train_data_path = config1['train_data_path']
        save_model_path = con + '/' + config1['save_model_path']
        savepath = con + '/' + config1['saveaxpath']
        savepath2 = con + '/' + config1['saveaxpath2']
        saverocpath = con + '/' + config1['assesspath']
        # read the data
        train_loader, data = load_data(train_data_path)
        # initialize the model
        model = NeuralNetwork(input_dim, hidden_dim, num_layers, output_dim, activation_function)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
        # loss function
        criterion = CustomLoss()
        # optimizer
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)  # , weight_decay=0.01)
        # the scheduler of learning rate
        scheduler = ReduceLROnPlateau(optimizer, 'min', patience=10, factor=0.67)
        # start learning
        train(model, train_loader, criterion, optimizer, scheduler, save_model_path, data, weight, con)
        # read the model after stop
        model = load_model(model, save_model_path)
        # visualize the model
        visualize_model(model, data, savepath, savepath2, saverocpath)
        # check the accuracy
        r2 = accuracy(model, data)
        r = np.vstack((r, r2))

    # save the results
    rname = np.array(config0)
    rname = rname.reshape(-1, 1)
    print(rname, r[1:, :])
    result1 = np.hstack((rname, r[1:, :]))
    df = pd.DataFrame(result1)
    output_path = "output.csv"  # the file path of results
    df.to_csv(output_path, index=False)


if __name__ == '__main__':
    main()
