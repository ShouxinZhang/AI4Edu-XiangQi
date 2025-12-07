from .storage import HistoryStorage
import logging

logger = logging.getLogger(__name__)

class HistoryManager:
    def __init__(self, base_dir="data/history"):
        self.storage = HistoryStorage(base_dir)
        
    def save_game(self, game_data, mode="training"):
        """
        Save a completed game record.
        game_data should contain: id, winner, steps, timestamp, moves (optional), etc.
        """
        # specialized logic or validation could go here
        self.storage.append_game(game_data, mode)
        logger.info(f"Saved {mode} game {game_data.get('id', 'unknown')}")
        
    def get_recent_history(self, mode="training", limit=50):
        """
        Get recent games for a specific mode.
        """
        return self.storage.load_recent_games(mode, limit)
