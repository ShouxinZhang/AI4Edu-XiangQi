
import os
import torch
import numpy as np
from game import XiangqiGame
from model import XiangqiNet
from mcts import MCTS

def verify():
    print("Verifying installation...")
    print(f"Torch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    game = XiangqiGame()
    net = XiangqiNet()
    if torch.cuda.is_available():
        net.cuda()
    print("Model initialized.")
    
    mcts = MCTS(game, net, {'num_mcts_sims': 2, 'cpuct': 1.0})
    board = game.get_canonical_board()
    pi = mcts.get_action_prob(board)
    print("MCTS inference successful.")
    
    print("ALL SYSTEMS GO!")

if __name__ == "__main__":
    verify()
