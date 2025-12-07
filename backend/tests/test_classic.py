
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from classic.evaluation import evaluate_board
from classic.minimax import MinimaxSolver
from game import XiangqiGame

def test_evaluation():
    print("Testing Evaluation...")
    # Empty board (invalid but for testing function)
    board = np.zeros((10, 9), dtype=int)
    assert evaluate_board(board) == 0
    
    # Symmetric Board
    # Red Rook at (0, 0)
    # Black Rook at (9, 0) [Corresponds to Red's (0, 0)]
    board[0][0] = 5
    board[9][0] = -5
    score = evaluate_board(board)
    print(f"Symmetric Rooks Score: {score}")
    assert score == 0, "Symmetric positions should measure 0 advantage"
    
    # Pawn Advantage Test
    # Red Pawn Crossed River (y=5, x=4)
    board2 = np.zeros((10, 9), dtype=int)
    board2[5][4] = 7 
    score_crossed = evaluate_board(board2)
    
    # Red Pawn at Home (y=3, x=4)
    board3 = np.zeros((10, 9), dtype=int)
    board3[3][4] = 7 
    score_home = evaluate_board(board3)
    
    print(f"Pawn Crossed: {score_crossed}, Pawn Home: {score_home}")
    assert score_crossed > score_home, "Crossed pawn should be more valuable"

def test_minimax():
    print("Testing Minimax...")
    game = XiangqiGame()
    # Init board
    # Solver needs to propose a move
    solver = MinimaxSolver(game, depth=1)
    move = solver.get_best_move(game.get_canonical_board())
    print(f"Best Move found (D1): {move}")
    assert move is not None
    
    # Depth 2
    solver2 = MinimaxSolver(game, depth=2)
    move2 = solver2.get_best_move(game.get_canonical_board())
    print(f"Best Move found (D2): {move2}")
    assert move2 is not None

if __name__ == "__main__":
    test_evaluation()
    test_minimax()
    print("ALL Classic Tests Passed!")
