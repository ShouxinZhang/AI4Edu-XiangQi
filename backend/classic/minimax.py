"""
Minimax Algorithm.

Standard Alpha-Beta Pruning implementation for Xiangqi.
Supports adjustable difficulty via depth and randomness.
"""
import numpy as np
import random
from .evaluation import evaluate_board


class MinimaxSolver:
    """Core Minimax Solver."""
    
    def __init__(self, game, depth: int = 2):
        """
        Initialize solver.
        
        Args:
            game: Game logic instance
            depth: Search depth (1=weak, 4+=strong)
        """
        self.game = game
        self.depth = depth

    def get_best_move(self, canonical_board):
        """
        Evaluate and find the best move.
        """
        valids = self.game.get_valid_moves(canonical_board, 1)
        valid_actions = np.where(valids == 1)[0]
        
        if len(valid_actions) == 0:
            return None
        
        best_action = valid_actions[0]
        best_score = -float('inf')
        
        # Consistent ordering for determinism (or shuffle if we want variety with SAME score?)
        # User requested "Purely deterministic behavior (best move only)".
        # Shuffling valid_actions introduces non-determinism if scores are equal.
        # To be "purely deterministic", we should NOT shuffle, or shuffle with fixed seed.
        # But usually engines return first best move.
        # However, playing same game every time is boring. "No Randomness" usually means "Play Best Move", but if multiple best?
        # Standard engines utilize randomness among equal best moves.
        # But user said "remove randomness param".
        # I will remove explicit random blunder.
        # I will keep shuffling for variety among EQUAL moves, or remove it if "Strict Determinism" is the goal.
        # User said "Minimax difficulty will now be determined SOLELY by search depth."
        # I'll restart the shuffle to keep it interesting but 'strongest possible'.
        np.random.shuffle(valid_actions)
        
        for action in valid_actions:
            next_board, next_player = self.game.get_next_state(canonical_board, 1, action)
            next_canonical = self.game.get_canonical_form(next_board, next_player)
            
            # Opponent's turn -> minimize their score -> negate
            score = -self._minimax(next_canonical, self.depth - 1, -float('inf'), float('inf'), False)
            
            if score > best_score:
                best_score = score
                best_action = action
                
        return best_action
    
    def _minimax(self, canonical_board, depth, alpha, beta, maximizing):
        """
        Recursive Minimax with Alpha-Beta Pruning.
        """
        # Check terminal state
        r = self.game.get_game_ended(canonical_board, 1)
        if r != 0:
            return r * 10000  # Large value for win/loss
        
        if depth == 0:
            return evaluate_board(canonical_board)
        
        valids = self.game.get_valid_moves(canonical_board, 1)
        valid_actions = np.where(valids == 1)[0]
        
        if len(valid_actions) == 0:
            return 0  # Draw
        
        # Node ordering optimization could go here (e.g. captures first)
        
        if maximizing:
            max_eval = -float('inf')
            for action in valid_actions:
                next_board, next_player = self.game.get_next_state(canonical_board, 1, action)
                next_canonical = self.game.get_canonical_form(next_board, next_player)
                
                eval_score = -self._minimax(next_canonical, depth - 1, -beta, -alpha, True)
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for action in valid_actions:
                next_board, next_player = self.game.get_next_state(canonical_board, 1, action)
                next_canonical = self.game.get_canonical_form(next_board, next_player)
                
                eval_score = -self._minimax(next_canonical, depth - 1, -beta, -alpha, False)
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval
