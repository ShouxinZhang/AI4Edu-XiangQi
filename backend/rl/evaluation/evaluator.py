"""
RL Evaluator.

Automates benchmarking of RL models against baseline opponents.
"""
from typing import Dict, List, Union, Any
import logging
from .arena import Arena
from .players import MinimaxPlayer

logger = logging.getLogger(__name__)

class RLEvaluator:
    """Evaluates an RL Agent against graded Classic AI opponents."""
    
    def __init__(self, game, agent_player):
        """
        Args:
            game: Game instance
            agent_player: AlphaZeroPlayer instance
        """
        self.game = game
        self.agent = agent_player
        
    def evaluate(self, levels: List[Union[int, Dict[str, Any]]] = None, games_per_level: int = 10) -> Dict[str, Dict[str, Union[float, int]]]:
        """
        Run benchmarks against configured levels.
        
        Args:
            levels: List of classic AI configurations to test against.
                    Each item can be dict {name, depth} or int (depth).
            games_per_level: Number of games to play per level.
            
        Returns:
            Dictionary mapping Opponent Name to detailed results.
        """
        if levels is None:
            # Default Benchmarks (Deterministic via Depth)
            levels = [
                {'name': 'Level_1_Beginner', 'depth': 1},
                {'name': 'Level_2_Amateur', 'depth': 2},
                {'name': 'Level_3_Club', 'depth': 3},
            ]
            
        results = {}
        
        print(f"\n[Evaluator] Starting Benchmark ({games_per_level} games per level)...")
        
        for config in levels:
            if isinstance(config, int):
                # Simple depth
                name = f"Classic_D{config}"
                depth = config
            else:
                name = config['name']
                depth = config['depth']
                
            opponent = MinimaxPlayer(self.game, depth=depth)
            
            # Setup Arena
            # Agent is Player 1, Opponent is Player 2
            arena = Arena(self.agent, opponent, self.game)
            
            p1_wins, p2_wins, draws = arena.play_games(games_per_level, verbose=False)
            
            total = p1_wins + p2_wins + draws
            win_rate = p1_wins / total if total > 0 else 0.0
            
            # Log result
            print(f"vs {name:<15}: Wins={p1_wins}, Losses={p2_wins}, Draws={draws} | WinRate={win_rate:.1%}")
            
            results[name] = {
                'win_rate': win_rate,
                'wins': p1_wins,
                'losses': p2_wins,
                'draws': draws
            }
            
        return results
