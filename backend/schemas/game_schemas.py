"""
Pydantic models for API requests and responses.
"""
from pydantic import BaseModel
from typing import List, Tuple, Optional


class BoardRequest(BaseModel):
    """Request body for AI move calculation."""
    board: List[List[int]]
    player: int  # 1 for Red, -1 for Black
    difficulty: Optional[int] = None  # 1-4 Classic, None for AlphaZero


class MoveResponse(BaseModel):
    """Response body for AI move result."""
    start: Tuple[int, int]
    end: Tuple[int, int]


class TrainingUpdate(BaseModel):
    """Internal training update message."""
    type: str  # 'step' or 'game_end'
    data: dict


class SaveGameRequest(BaseModel):
    """Request body for saving a game."""
    mode: str  # 'pvp', 'pve', 'training'
    winner: int  # 1 = Red, -1 = Black, 0 = Draw
    moves: list  # List of moves [[from, to], ...]
    timestamp: float = None


class TrainingStartRequest(BaseModel):
    """Configuration for starting training."""
    max_steps: int = 200
    workers: int = 4
    mode: str = "parallel"  # "single" or "parallel"
    num_mcts_sims: int = 25
    num_episodes: int = 10
