"""Evaluation subpackage - Evaluation tools.

Classes:
    - Arena: Game arena for player evaluation
    - RLEvaluator: Automated benchmark suite
    - RandomPlayer, AlphaZeroPlayer, MinimaxPlayer: Player implementations
"""
from .arena import Arena
from .evaluator import RLEvaluator
from .players import RandomPlayer, AlphaZeroPlayer, MinimaxPlayer
