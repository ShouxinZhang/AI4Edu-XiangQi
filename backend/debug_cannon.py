
import numpy as np
from game import XiangqiGame

def test_cannon_bug():
    game = XiangqiGame()
    board = game._init_board()
    
    # Moves from log
    # Move 1: [5,9] -> [4,8] (Red Advisor)
    move1 = ((5,9), (4,8))
    print(f"Applying Move 1: {move1}")
    game.make_move(move1)
    
    # Move 2: [1,2] -> [1,4] (Black Cannon)
    move2 = ((1,2), (1,4))
    print(f"Applying Move 2: {move2}")
    game.make_move(move2)
    
    # Move 3: [1,7] -> [1,5] (Red Cannon)
    move3 = ((1,7), (1,5))
    print(f"Applying Move 3: {move3}")
    game.make_move(move3)
    
    # Now it's Black's turn (Player -1)
    print(f"Current Player: {game.current_player}")
    
    # Get Canonical Board
    canonical_board = game.get_canonical_form(game.board, game.current_player)
    
    print("\nChecking Canonical Board at x=7 column:")
    # In Canonical (Black perspective):
    # (7,7) should be Black Cannon (Own)
    # (7,6) should be Black Pawn (Own)
    # (7,3) should be Red Pawn (Enemy)
    # (7,2) should be Red Cannon (Enemy)
    # (7,0) should be Red Horse (Enemy)
    
    for y in range(10):
        p = canonical_board[y][7]
        print(f"({7},{y}): {p}")
        
    # Check valid moves for Cannon at (7,7)
    # We need to use a temp game like get_valid_moves does
    temp_game = XiangqiGame()
    temp_game.board = np.copy(canonical_board)
    temp_game.current_player = 1
    
    print("\nCalculating moves for piece at (7,7)...")
    moves = temp_game._get_cannon_moves(7, 7)
    print(f"Found {len(moves)} moves:")
    for m in moves:
        print(m)
        
    # Specifically check if (7,7)->(7,0) is in moves
    target_move = ((7,7), (7,0))
    if target_move in moves:
        print("\n❌ BUG CONFIRMED: Illegal move (7,7)->(7,0) is valid!")
    else:
        print("\n✅ Logic correct: Illegal move not found.")

if __name__ == "__main__":
    test_cannon_bug()
