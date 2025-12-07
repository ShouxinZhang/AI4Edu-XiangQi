import json
import os
import time

class HistoryStorage:
    def __init__(self, base_dir="data/history"):
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            
    def _get_filename(self, mode):
        # Organize by mode (training, pvp, pve)
        return os.path.join(self.base_dir, f"{mode}_games.jsonl")

    def append_game(self, game_record, mode="training"):
        filename = self._get_filename(mode)
        with open(filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(game_record) + "\n")
            
    def load_recent_games(self, mode="training", limit=50):
        filename = self._get_filename(mode)
        if not os.path.exists(filename):
            return []
            
        # Efficiently read last N lines? 
        # For simplicity in this demo, read all and slice. 
        # Production would use seek() or a DB.
        games = []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Parse last 'limit' lines in reverse order
                for line in reversed(lines[-limit:]):
                    try:
                        games.append(json.loads(line))
                    except: pass
        except Exception as e:
            print(f"Error loading history: {e}")
            
        return games
