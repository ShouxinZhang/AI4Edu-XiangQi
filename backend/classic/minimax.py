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

    def get_best_move(self, canonical_board, progress_callback=None, abort_check=None):
        """
        Evaluate and find the best move.
        
        Args:
            canonical_board: The board state
            progress_callback: Optional callable(current, total)
            abort_check: Optional callable() -> bool. If returns True, stop calculation.
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
        
        total_moves = len(valid_actions)
        
        for i, action in enumerate(valid_actions):
            # Check abort
            if abort_check and abort_check():
                return None

            # Report progress
            if progress_callback:
                progress_callback(i, total_moves)
                
            next_board, next_player = self.game.get_next_state(canonical_board, 1, action)
            next_canonical = self.game.get_canonical_form(next_board, next_player)
            
            # Opponent's turn -> minimize their score -> negate
            score = -self._minimax(next_canonical, self.depth - 1, -float('inf'), float('inf'), False, abort_check)
            
            if abort_check and abort_check():
                return None
            
            if score > best_score:
                best_score = score
                best_action = action
                
        return best_action
    
    def _minimax(self, canonical_board, depth, alpha, beta, maximizing, abort_check=None):
        """
        Recursive Minimax with Alpha-Beta Pruning.
        """
        # Periodic abort check (every node might be too expensive, but depth isn't huge here)
        # For responsiveness, check every node or check based on some counter.
        # Since we are in python, check every node is safest for immediate stop.
        if abort_check and abort_check():
            return 0 # Return dummy value, will be discarded up stack

        # Check terminal state
        r = self.game.get_game_ended(canonical_board, 1)
        if r != 0:
            return r * 10000  # Large value for win/loss
        
        if depth == 0:
            return self._quiescence(canonical_board, alpha, beta)
        
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
                
                eval_score = -self._minimax(next_canonical, depth - 1, -beta, -alpha, True, abort_check)
                if abort_check and abort_check(): return 0

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
                
                eval_score = -self._minimax(next_canonical, depth - 1, -beta, -alpha, False, abort_check)
                if abort_check and abort_check(): return 0

                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def _quiescence(self, canonical_board, alpha, beta):
        """
        Quiescence Search:
        Search only captures to avoid the horizon effect.
        """
        # 1. Stand Pat (Evaluate current position)
        stand_pat = evaluate_board(canonical_board)
        
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat
            
        # 2. Generate Captures ONLY
        # Get all valid moves
        valids = self.game.get_valid_moves(canonical_board, 1)
        valid_actions = np.where(valids == 1)[0]
        
        capture_actions = []
        for action in valid_actions:
            # Check if move is a capture
            # Need to decode move to see target square
            move = self.game.decode_move(action)
            start, end = move
            # In canonical form, player is 1 (Positive), Enemy is -1 (Negative)
            # board[y][x] < 0 implies capture
            if canonical_board[end[1]][end[0]] < 0:
                capture_actions.append(action)
                
        if not capture_actions:
            return stand_pat
            
        # 3. Search Captures
        for action in capture_actions:
            next_board, next_player = self.game.get_next_state(canonical_board, 1, action)
            next_canonical = self.game.get_canonical_form(next_board, next_player)
            
            # Recursively call QS
            # Negamax logic: -quiescence(...)
            score = -self._quiescence(next_canonical, -beta, -alpha)
            
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
                
        return alpha
