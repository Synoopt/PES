"""
Training loop utilities.

Training loop utilities: contains training functions and model saving.
"""

import torch
from utils import setup_logging, log_metrics
import numpy as np
from sklearn.metrics import r2_score
from tqdm import tqdm

def train(
    model,
    train_loader,
    criterion,
    optimizer,
    scheduler,
    path,
    data,
    weight,
    trainname,
    epochs: int = 1000,
    patience: int = 50,
    min_delta: float = 1e-4,
):
    """
    Train the model with early stopping and LR scheduling.

    Train model using early stopping and learning rate scheduling.

    Args:
        model: torch model / Model
        train_loader: DataLoader producing (X, y) / Training data loader
        criterion: loss function / Loss function
        optimizer: optimizer / Optimizer
        scheduler: LR scheduler / Learning rate scheduler
        path (str): checkpoint save path / Model save path
        data (pd.DataFrame): raw dataframe for eval / Data for evaluation and visualization
        weight (float): gradient term weight / Gradient term weight
        trainname (str): run name for logging / Training task name
        epochs (int): max epochs / Maximum epochs
        patience (int): early stopping patience / Early stopping patience value
        min_delta (float): min improvement to reset patience / Minimum improvement to reset patience
    """
    torch.set_num_threads(12)
    trainname = ''.join(['Training Batch'])
    writer = setup_logging(trainname)
    model.train()
    best_loss = float('inf')
    patience_counter = 0
    # min improvement to reset patience
    min_delta = float(min_delta)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    epochs = int(epochs)
    current_lr = optimizer.param_groups[0]['lr']  # the initial learning rate
    loss_list = []
    for epoch in tqdm(range(epochs),desc=trainname):
        sum_total = 0
        grad_list = torch.tensor([[0.,0.,0.]], dtype=torch.float32, device=device)
        model.train()  # assure the model is in training mode
        for inputs, labels in train_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            inputs.retain_grad()
            outputs.backward(torch.ones_like(outputs), retain_graph=True)
            predicted_gradients = inputs.grad/0.529
            optimizer.zero_grad()
            outputs = model(inputs)
            F1 = -predicted_gradients[0][0]
            F2 = predicted_gradients[0][0]-predicted_gradients[0][1]
            F3 = predicted_gradients[0][1]
            pred_grad = torch.cat((F2.reshape(-1,1),F3.reshape(-1,1),F1.reshape(-1,1)),dim=1).to(device)
            loss = criterion(outputs[0][0], labels[0][0],pred_grad, labels[0][1:4], weight).to(device)
            grad_list = torch.cat((grad_list,pred_grad),dim=0)     
            grad_list = grad_list.to(device)
            loss.backward()
            sum_total += loss
            optimizer.step()
        sum_total /= len(train_loader)
        loss_list.append(sum_total)
        epsilon = 1e-6
        # Detect gradient vanishing to avoid futile training.
        # Detect gradient vanishing to avoid futile training.
        if torch.all(grad_list.abs().mean() < epsilon):
            print('break')
            break
        
        model.eval()
        X_pred = np.array([data['x'].to_numpy(), data['y'].to_numpy()]).T
        X_pred_tensor = torch.tensor(X_pred, dtype=torch.float32).to(device)

        # Predict on full mesh for logging.
        # Make predictions on full data for logging.
        with torch.no_grad():  # excluding the gradient
            y_pred_tensor = model(X_pred_tensor).cpu()

        # Convert the prediction results to a NumPy array.
        y_pred = y_pred_tensor.numpy()

        r_squared = r2_score(data['z1'], y_pred)
        
        log_metrics(writer, {'Loss': sum_total, 'Accuracy': r_squared}, epoch, "Train")

        new_lr = optimizer.param_groups[0]['lr']
        if new_lr < current_lr:
            current_lr = new_lr  # upgrade the learning rate

        # Update the best checkpoint if improved.
        # If loss improves, save the best model.
        if sum_total < best_loss - min_delta:
            best_loss = sum_total
            patience_counter = 0  # reset the patience counter
            save_model(model, path)
        else:
            patience_counter += 1 # if no improvements, add 1 to the patience counter
        
        #optimize the learning rate
        scheduler.step(sum_total.detach().cpu().item())
        # check the early stop condition
        if patience_counter >= patience:
            tqdm.write("Early stopping triggered")
            break

def save_model(model, path):
    """
    Save model state dict to disk.

    Save model weights to disk.
    """
    torch.save(model.state_dict(), path)


