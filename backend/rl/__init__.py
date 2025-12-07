"""
RL (Reinforcement Learning) Module for Xiangqi AI.

This package contains all RL-related components:

Submodules:
    - rl.config: Configuration management (RLConfig)
    - rl.models: Neural network architectures (XiangqiNet, ResBlock)
    - rl.algorithms: Search algorithms (MCTS)
    - rl.training: Training utilities (XiangqiDataset, GameLogger, BroadcastClient)
    - rl.evaluation: Evaluation tools (Arena, Players, Metrics)
    - rl.workers: Parallel self-play workers (PredictionServer, SelfPlayWorker)
    - rl.utils: Checkpoint management

Usage:
    from rl.config import RLConfig
    from rl.models import XiangqiNet
    from rl.algorithms import MCTS
"""
