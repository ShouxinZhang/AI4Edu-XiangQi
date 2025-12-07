"""
Unified Configuration for RL Training.

Centralizes all hyperparameters and settings that were previously
scattered across train.py, train_parallel.py, and server.py.
"""
import torch
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RLConfig:
    """Configuration for RL training and inference."""
    
    # Training iterations
    num_iters: int = 1000
    num_eps: int = 10  # Episodes per iteration
    
    # MCTS parameters
    num_mcts_sims: int = 25
    cpuct: float = 1.0
    
    # Temperature for action selection
    temp_threshold: int = 15  # Use temp=1 for first N moves, then temp=0
    
    # Neural network training
    lr: float = 0.001
    epochs: int = 10
    batch_size: int = 512
    
    # Parallel training
    num_workers: int = 4
    
    # Paths
    checkpoint_dir: str = './checkpoints'
    data_dir: str = './data'
    evolution_log_dir: str = './data/evolution'
    
    # Hardware
    cuda: bool = field(default_factory=lambda: torch.cuda.is_available())
    
    # Server endpoint for broadcasting training updates
    broadcast_url: str = "http://localhost:8000/internal/training/update"
    
    def to_dict(self) -> dict:
        """Convert config to dictionary for backward compatibility."""
        return {
            'num_iters': self.num_iters,
            'num_eps': self.num_eps,
            'num_mcts_sims': self.num_mcts_sims,
            'cpuct': self.cpuct,
            'tempThreshold': self.temp_threshold,
            'lr': self.lr,
            'epochs': self.epochs,
            'batch_size': self.batch_size,
            'num_workers': self.num_workers,
            'checkpoint': self.checkpoint_dir,
            'cuda': self.cuda,
        }


# Default global config instance
default_config = RLConfig()
