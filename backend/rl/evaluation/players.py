"""
Player Implementations for Xiangqi.

Contains various player types for evaluation and gameplay:
- RandomPlayer: Random valid moves
- AlphaZeroPlayer: MCTS + Neural Network
- MinimaxPlayer: Wrapper around classic Minimax solver
"""
import numpy as np

# Import Minimax from generalized classic algorithms
from classic.minimax import MinimaxSolver


class RandomPlayer:
    """A player that makes random valid moves."""
    
    def __init__(self, game):
        self.game = game
    
    def __call__(self, canonical_board):
        valids = self.game.get_valid_moves(canonical_board, 1)
        valid_actions = np.where(valids == 1)[0]
        return np.random.choice(valid_actions)


class AlphaZeroPlayer:
    """A player powered by MCTS + Neural Network."""
    
    def __init__(self, game, nnet, args, temp=0):
        from ..algorithms.mcts import MCTS
        self.game = game
        self.nnet = nnet
        self.args = args
        self.temp = temp
        self.mcts = MCTS(game, nnet, args)
    
    def __call__(self, canonical_board):
        pi = self.mcts.get_action_prob(canonical_board, temp=self.temp)
        return np.argmax(pi)


class MinimaxPlayer:
    """
    Wrapper for the classic Minimax solver to be used in Arena.
    """
    
    def __init__(self, game, depth: int = 2):
        self.solver = MinimaxSolver(game, depth=depth)
    
    def __call__(self, canonical_board):
        """
        Given a canonical board, return the best action.
        """
        action = self.solver.get_best_move(canonical_board)
        return action if action is not None else 0
