"""
Custom loss combining value MSE and gradient MSE.

Custom loss: weighted sum of predicted value MSE and gradient MSE.
"""

import torch
import torch.nn as nn
class CustomLoss(nn.Module):
    def __init__(self):
        super(CustomLoss, self).__init__()
    
    def forward(self, input, target, dY_dX_pred, dY_dX_target, weight):
        """
        Compute weighted sum of output error and gradient error.

        Compute weighted sum of output error and gradient error.
        """
        # the main loss based on the MSE of the input and output
        loss_output = torch.mean((input - target) ** 2)*(1-weight)
        
        # the added loss based on MSE of derivatives of the input and output
        loss_derivative = torch.mean((dY_dX_pred - dY_dX_target) ** 2) * weight

        # combine 2 different loss
        loss = loss_output + loss_derivative
        return loss
