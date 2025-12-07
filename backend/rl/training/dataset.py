"""
Dataset for Xiangqi Training.

PyTorch Dataset for training examples generated from self-play.
"""
import torch
from torch.utils.data import Dataset


class XiangqiDataset(Dataset):
    """
    PyTorch Dataset for Xiangqi training examples.
    
    Each example is a tuple of (board_state, policy, value).
    """
    
    def __init__(self, examples):
        """
        Initialize dataset.
        
        Args:
            examples: List of (board_tensor, policy, value) tuples
        """
        self.examples = examples
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        board, pi, v = self.examples[idx]
        return (
            torch.FloatTensor(board),
            torch.FloatTensor(pi),
            torch.FloatTensor([v])
        )
