"""
Unified Training Entry Point for RL Module.

Supports both single-machine (Coach) and parallel (ParallelTrainer) modes.

Usage:
    python -m rl.train --mode single
    python -m rl.train --mode parallel --workers 4
"""
import sys
import argparse
import torch

from game import XiangqiGame
from .models.xiangqi_net import XiangqiNet
from .training.coach import Coach
from .training.parallel_trainer import ParallelTrainer
from .utils.checkpoint import get_latest_checkpoint, load_checkpoint
from .config import RLConfig

def parse_args():
    parser = argparse.ArgumentParser(description='Xiangqi AlphaZero Training')
    parser.add_argument('--mode', type=str, choices=['single', 'parallel'], default='single',
                        help='Training mode: single or parallel')
    parser.add_argument('--workers', type=int, default=4,
                        help='Number of workers for parallel training')
    parser.add_argument('--checkpoint', type=str, default='./checkpoints',
                        help='Checkpoint directory')
    parser.add_argument('--no-cuda', action='store_true', help='Disable CUDA')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Base Configuration
    # In a real scenario, we might want to load this from a config file or RLConfig default
    # For now, we use a dictionary similar to previous scripts but we can map arguments to it.
    
    config = {
        'num_iters': 1000,
        'num_eps': 10,
        'tempThreshold': 15,
        'updateThreshold': 0.6,
        'maxlenOfQueue': 200000,
        'num_mcts_sims': 25,
        'cpuct': 1.0,
        'checkpoint': args.checkpoint,
        'lr': 0.001,
        'dropout': 0.3,
        'epochs': 10,
        'batch_size': 512,
        'cuda': not args.no_cuda and torch.cuda.is_available(),
        'num_channels': 512,
        'num_workers': args.workers
    }
    
    # Initialize Game and Model
    # Note: Game is stateless logic mostly, but Coach needs an instance
    # ParallelTrainer might instantiate its own games in workers
    game = XiangqiGame() 
    nnet = XiangqiNet()
    
    if config['cuda']:
        nnet.cuda()
    
    # Resume Logic
    checkpoint_path, start_iter = get_latest_checkpoint(config['checkpoint'])
    if checkpoint_path:
        print(f"[Resume] Loading checkpoint: {checkpoint_path} (iteration {start_iter})")
        start_iter = load_checkpoint(checkpoint_path, nnet)
    else:
        print("[Resume] No checkpoint found, starting from scratch.")
        start_iter = 0

    print(f"=== Starting Training in [{args.mode.upper()}] mode ===")
    
    if args.mode == 'single':
        coach = Coach(game, nnet, config)
        coach.start_iteration = start_iter + 1
        coach.learn()
        
    elif args.mode == 'parallel':
        # ParallelTrainer expects the Game Class, not instance (for pickling/spawning)
        # But wait, our extracted ParallelTrainer code:
        # trainer = ParallelTrainer(XiangqiGame, model, args)
        # It takes the class.
        
        trainer = ParallelTrainer(XiangqiGame, nnet, config)
        trainer.start_iteration = start_iter + 1
        trainer.learn()

if __name__ == "__main__":
    main()
