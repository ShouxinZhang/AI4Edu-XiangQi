"""
Arena for Evaluating AI Players.

Two players compete in multiple games to determine win rates.
Used to measure training progress.
"""
import numpy as np
from tqdm import tqdm


class Arena:
    """
    Facilitates games between two players to evaluate performance.
    """
    
    def __init__(self, player1, player2, game, display=None):
        """
        Initialize arena.
        
        Args:
            player1: Callable that takes (canonical_board) and returns action
            player2: Callable that takes (canonical_board) and returns action
            game: Game instance
            display: Optional function to display the board
        """
        self.player1 = player1
        self.player2 = player2
        self.game = game
        self.display = display

    def play_game(self, verbose=False):
        """
        Play a single game.
        
        Returns:
            1 if player1 wins
            -1 if player2 wins
            0 for draw
        """
        board = self.game._init_board()
        current_player = 1  # 1 for player1, -1 for player2
        step = 0
        max_steps = 200

        players = {1: self.player1, -1: self.player2}
        
        while step < max_steps:
            step += 1
            canonical_board = self.game.get_canonical_form(board, current_player)
            
            action = players[current_player](canonical_board)
            
            board, current_player = self.game.get_next_state(board, current_player, action)
            
            if verbose and self.display:
                self.display(board)
            
            # Check game end
            r = self.game.get_game_ended(board, current_player)
            if r != 0:
                return -r * current_player  # Normalize to player1's perspective

        return 0  # Draw
    
    def play_games(self, num_games, verbose=False):
        """
        Play multiple games.
        
        Args:
            num_games: Number of games to play
            verbose: Whether to display boards
            
        Returns:
            Tuple of (player1_wins, player2_wins, draws)
        """
        p1_wins = 0
        p2_wins = 0
        draws = 0
        
        for _ in tqdm(range(num_games), desc="Arena Games"):
            result = self.play_game(verbose=verbose)
            if result == 1:
                p1_wins += 1
            elif result == -1:
                p2_wins += 1
            else:
                draws += 1
                
        return p1_wins, p2_wins, draws
