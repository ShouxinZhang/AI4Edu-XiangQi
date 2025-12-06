
import torch
import torch.nn as nn
import torch.nn.functional as F

class ResBlock(nn.Module):
    def __init__(self, channels):
        super(ResBlock, self).__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x):
        residual = x
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.bn2(self.conv2(x))
        x += residual
        x = F.relu(x)
        return x

class XiangqiNet(nn.Module):
    def __init__(self, board_height=10, board_width=9, num_res_blocks=10, num_channels=256, action_size=8100):
        super(XiangqiNet, self).__init__()
        self.board_height = board_height
        self.board_width = board_width
        self.num_channels = num_channels
        
        # Initial Conv Block
        self.conv_input = nn.Conv2d(14, num_channels, kernel_size=3, padding=1)
        self.bn_input = nn.BatchNorm2d(num_channels)
        
        # Residual Tower
        self.res_tower = nn.Sequential(
            *[ResBlock(num_channels) for _ in range(num_res_blocks)]
        )
        
        # Policy Head
        self.conv_policy = nn.Conv2d(num_channels, 2, kernel_size=1)
        self.bn_policy = nn.BatchNorm2d(2)
        self.fc_policy = nn.Linear(2 * board_height * board_width, action_size)
        
        # Value Head
        self.conv_value = nn.Conv2d(num_channels, 1, kernel_size=1)
        self.bn_value = nn.BatchNorm2d(1)
        self.fc_value1 = nn.Linear(1 * board_height * board_width, 256)
        self.fc_value2 = nn.Linear(256, 1)

    def forward(self, x):
        # x: (N, 14, 10, 9)
        x = F.relu(self.bn_input(self.conv_input(x)))
        x = self.res_tower(x)
        
        # Policy Head
        p = F.relu(self.bn_policy(self.conv_policy(x)))
        p = p.view(p.size(0), -1)
        p = self.fc_policy(p) # Logits, softmax will be applied later
        
        # Value Head
        v = F.relu(self.bn_value(self.conv_value(x)))
        v = v.view(v.size(0), -1)
        v = F.relu(self.fc_value1(v))
        v = torch.tanh(self.fc_value2(v))
        
        return F.log_softmax(p, dim=1), v

    def predict(self, board_tensor, device='cuda'):
        # Helper for inference
        self.eval()
        with torch.no_grad():
            x = torch.FloatTensor(board_tensor).unsqueeze(0).to(device)
            log_pi, v = self.forward(x)
            return torch.exp(log_pi).cpu().numpy()[0], v.cpu().numpy()[0][0]
