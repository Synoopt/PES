"""
Custom loss combining value MSE and gradient MSE.

自定义损失：预测值的 MSE 与梯度的 MSE 按权重加权求和。
"""

import torch
import torch.nn as nn
class CustomLoss(nn.Module):
    def __init__(self):
        super(CustomLoss, self).__init__()
    
    def forward(self, input, target, dY_dX_pred, dY_dX_target, weight):
        """
        Compute weighted sum of output error and gradient error.

        计算输出误差与梯度误差的加权和。
        """
        # the main loss based on the MSE of the input and output
        loss_output = torch.mean((input - target) ** 2)*(1-weight)
        
        # the added loss based on MSE of derivatives of the input and output
        loss_derivative = torch.mean((dY_dX_pred - dY_dX_target) ** 2) * weight

        # combine 2 different loss
        loss = loss_output + loss_derivative
        return loss
