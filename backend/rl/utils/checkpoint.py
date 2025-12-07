"""
Checkpoint Utilities for Resume Training.

Provides functions to save, load, and find the latest model checkpoints.
"""
import os
import re
import torch
import logging

logger = logging.getLogger(__name__)


def save_checkpoint(folder: str, filename: str, state_dict, optimizer_state=None, iteration=None):
    """
    Save a model checkpoint.
    
    Args:
        folder: Directory to save checkpoint
        filename: Checkpoint filename
        state_dict: Model state dictionary
        optimizer_state: Optional optimizer state
        iteration: Optional iteration number
    """
    filepath = os.path.join(folder, filename)
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    checkpoint = {
        'state_dict': state_dict,
        'iteration': iteration
    }
    if optimizer_state is not None:
        checkpoint['optimizer'] = optimizer_state
        
    torch.save(checkpoint, filepath)
    logger.info(f"Checkpoint saved: {filepath}")


def load_checkpoint(filepath: str, model, optimizer=None) -> int:
    """
    Load a checkpoint into a model (and optionally an optimizer).
    
    Args:
        filepath: Path to checkpoint file
        model: Model to load weights into
        optimizer: Optional optimizer to load state into
        
    Returns:
        Iteration number from the checkpoint, or 0 if not found
    """
    if not os.path.exists(filepath):
        logger.warning(f"Checkpoint not found: {filepath}")
        return 0
        
    checkpoint = torch.load(filepath)
    model.load_state_dict(checkpoint['state_dict'])
    
    if optimizer is not None and 'optimizer' in checkpoint:
        optimizer.load_state_dict(checkpoint['optimizer'])
        
    iteration = checkpoint.get('iteration', 0)
    logger.info(f"Checkpoint loaded: {filepath} (iteration {iteration})")
    return iteration


def get_latest_checkpoint(folder: str):
    """
    Find the latest checkpoint_N.pth.tar in the given folder.
    
    Args:
        folder: Directory containing checkpoints
        
    Returns:
        Tuple of (filepath, iteration) or (None, 0) if no checkpoint found
    """
    if not os.path.exists(folder):
        return None, 0
        
    pattern = re.compile(r"checkpoint_(\d+)\.pth\.tar")
    max_iter = 0
    best_file = None
    
    for filename in os.listdir(folder):
        match = pattern.match(filename)
        if match:
            iter_num = int(match.group(1))
            if iter_num > max_iter:
                max_iter = iter_num
                best_file = os.path.join(folder, filename)
                
    return best_file, max_iter
