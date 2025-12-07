"""
Game Logger for Training Evolution.

Logs game records during training for analysis and visualization.
"""
import os
import json
import datetime


class GameLogger:
    """
    Logs training games to disk for analysis.
    
    Creates JSON files with game records including moves, winner, and metadata.
    """
    
    def __init__(self, log_dir: str = "data/evolution"):
        """
        Initialize logger.
        
        Args:
            log_dir: Directory to save game logs
        """
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def log_game(self, iteration: int, game_record: dict):
        """
        Log a single game.
        
        Args:
            iteration: Training iteration number
            game_record: Dict with game_id, moves, winner, timestamp, etc.
        """
        filename = os.path.join(
            self.log_dir, 
            f"game_{iteration}_{game_record.get('game_id', 'unknown')}.json"
        )
        with open(filename, 'w') as f:
            json.dump(game_record, f, indent=2)
