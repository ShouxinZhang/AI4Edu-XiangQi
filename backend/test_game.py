
from game import XiangqiGame, BOARD_HEIGHT, BOARD_WIDTH
import numpy as np

def print_board(game):
    symbols = {
        0: '.', 
        1: 'K', 2: 'A', 3: 'E', 4: 'H', 5: 'R', 6: 'C', 7: 'P',
        -1: 'k', -2: 'a', -3: 'e', -4: 'h', -5: 'r', -6: 'c', -7: 'p'
    }
    print("  0 1 2 3 4 5 6 7 8")
    for y in range(BOARD_HEIGHT):
        line = f"{y} "
        for x in range(BOARD_WIDTH):
            line += symbols[game.board[y][x]] + " "
        print(line)
    print()

def test_moves():
    game = XiangqiGame()
    print("Initial Board:")
    print_board(game)
    
    moves = game.get_legal_moves()
    print(f"Initial legal moves: {len(moves)}")
    
    # Try a specific move: Cannon to middle (C2=5) aka C8=5
    # Red Cannon at (1, 2) moving to (4, 2)
    # Note: My init: Red at top y=0..3. Red Cannons at (1, 2) and (7, 2).
    # Wait, in standard Xiangqi setup:
    # Red (South, usually bottom) vs Black (North, usually top).
    # But my init code: 
    # Red pieces at y=0 (K, A, E, H, R), y=2 (C), y=3 (P). This means Red is at TOP (low y).
    # Black pieces at y=9 (k...), y=7 (c), y=6 (p). Black is at BOTTOM (high y).
    # This is reversed from standard "Red at Bottom" but consistent internally.
    
    # Red Cannon at (1, 2). Target (4, 2).
    move = ((1, 2), (4, 2))
    assert move in moves, "Cannon to middle should be valid"
    
    game.make_move(move)
    print("After Red Cannon move:")
    print_board(game)
    
    # Now Black's turn. Black piece at y=7.
    # Black Cannon at (1, 7) moving to (4, 7).
    blk_move = ((1, 7), (4, 7)) # x=1, y=7 -> x=4, y=7
    moves = game.get_legal_moves()
    assert blk_move in moves, "Black Cannon move should be valid"
    
    game.make_move(blk_move)
    print("After Black Cannon move:")
    print_board(game)
    
    print("Test Validated!")

if __name__ == "__main__":
    test_moves()
