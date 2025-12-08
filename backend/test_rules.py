
import sys
import os
import unittest
import numpy as np

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game import XiangqiGame, BOARD_HEIGHT, BOARD_WIDTH, RED, BLACK, KING, ROOK, CANNON, PAWN

class TestXiangqiRules(unittest.TestCase):
    def setUp(self):
        self.game = XiangqiGame()
        # Clear board for custom setup
        self.game.board = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=int)

    def test_suicide_move_rejection(self):
        print("\nTesting Suicide Move Rejection...")
        # Setup: Red King at (4,9), Black Rook at (4,0)
        # Red King tries to move to (3,9), but (3,9) is attacked by Black Rook 2 at (3,0)
        self.game.board[9][4] = KING # Red King
        self.game.board[0][3] = -ROOK # Black Rook
        
        # Current state: King is safe at (4,9).
        # Move King to (3,9) -> (3,9) is in file 3. 
        # Black Rook at (3,0) attacks file 3.
        # So moving to (3,9) should be suicide.
        
        self.game.current_player = RED
        moves = self.game.get_legal_moves()
        
        # Check if move ((4,9), (3,9)) is present
        suicide_move = ((4,9), (3,9))
        self.assertNotIn(suicide_move, moves, "Suicide move should be rejected")
        print("PASS: Suicide move rejected.")

    def test_flying_general_rejection(self):
        print("\nTesting Flying General Rejection...")
        # Setup: Red King at (4,9), Black King at (4,0)
        # Red King moves to (3,9) -> OK
        # But wait, let's set up a scenario where moving a piece exposes the King to Flying General.
        
        self.game.board[9][4] = KING
        self.game.board[0][4] = -KING
        self.game.board[5][4] = PAWN # Red Pawn blocking
        
        # Red moves Pawn away from (4,5) to (3,5)
        # This exposes Red King to Black King. Should be illegal.
        self.game.current_player = RED
        moves = self.game.get_legal_moves()
        
        flying_gen_move = ((4,5), (3,5))
        self.assertNotIn(flying_gen_move, moves, "Move exposing Flying General should be rejected")
        print("PASS: Flying General exposed move rejected.")

    def test_checkmate_detection(self):
        print("\nTesting Checkmate Detection...")
        # Setup: Red King at (4,9) trapped by Black Rooks
        # Black Rook at (4,0) -> Checking
        # Black Rook at (3,0) -> Covering left
        # Black Rook at (5,0) -> Covering right
        # Red King has no Advisors/Elephants to block.
        
        self.game.board[9][4] = KING
        self.game.board[0][4] = -ROOK
        self.game.board[0][3] = -ROOK
        self.game.board[0][5] = -ROOK
        
        # Must add Black King to prevent "Victory" detection
        self.game.board[0][8] = -KING # Far away corner
        
        self.game.current_player = RED
        moves = self.game.get_legal_moves()
        self.assertEqual(len(moves), 0, "Should have no legal moves in Checkmate")
        
        # Verify get_game_ended
        # get_game_ended takes a CANONICAL board.
        # Check logic:
        # board is canonical (Red perspective).
        # get_game_ended(board, 1) should return -1 (Loss)
        
        canonical_board = self.game.get_canonical_form(self.game.board, RED)
        result = self.game.get_game_ended(canonical_board, RED)
        self.assertEqual(result, -1, "Game should end with Loss (-1)")
        print("PASS: Checkmate detected as Loss.")

    def test_stalemate_detection(self):
        print("\nTesting Stalemate Detection...")
        # Setup: Red King at (4,9) NOT IN CHECK, but no legal moves.
        # Pinned by Rooks but not attacked directly?
        # Hard to set up pure stalemate for King without other pieces.
        # Let's trap King in corner? No, King restricted to palace.
        # Let's say King at (4,9).
        # Black Pawn at (4,8) (Head of King) -> Check.
        
        # Try a "Stalemate" (困毙).
        # Red King at (3,9).
        # Black King at (3,0). Flying general prevents move to (3,x).
        # Wait, if Kings face each other directly, it's Flying General.
        # Stalemate is: No moves, but NOT in check.
        
        # Setup:
        # Red King at (3,9) (Left bottom corner of palace).
        # Adjacents blocked by own pieces (trapped).
        # Own Pawn at (4,9) -> Blocks right.
        # Own Pawn at (3,8) -> Blocks up.
        # No Check. Make sure enemies don't attack (3,9).
        
        self.game.board[9][3] = KING
        self.game.board[9][4] = PAWN # Block Right
        self.game.board[8][3] = PAWN # Block Up
        
        # Verify no check
        self.game.current_player = RED
        self.assertFalse(self.game.is_in_check(RED), "Red should not be in check")
        
        # Verify no moves for King
        # Pawns also blocked? (Pawns move forward/sideways).
        # Red Pawn at (9,4) can move to (8,4)? Yes.
        # We need to freeze ALL pieces.
        
        # Simplest Stalemate:
        # Red King isolated.
        # Black Rooks control all escape squares but don't attack King directly.
        
        self.game.board = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=int)
        self.game.board[9][3] = KING # Corner of palace
        
        # Black Rook at (4,0) controls file 4 (blocked by wall), file 3 is King.
        # Black Rook at (0,8) controls rank 8.
        # King at (3,9) can move to:
        # (4,9) -> controlled by ...
        # (3,8) -> controlled by Rook on rank 8.
        
        self.game.board[8][0] = -ROOK # Controls Rank 8 (prevents moving UP)
        self.game.board[0][4] = -ROOK # Controls File 4 (prevents moving RIGHT)
        
        # Must add Black King
        self.game.board[0][0] = -KING
        # King is at (3,9).
        # Move to (3,8): Attacked by Rook at (8,0)? No, Rook at (8,0) covers (8,x). Correct.
        # Move to (4,9): Attacked by Rook at (0,4) covers (x,4). Correct.
        
        # So King is at (3,9).
        # (3,8) is attacked.
        # (4,9) is attacked.
        # King is NOT at (3,9).
        # Wait, if King is at (3,9), is it attacked?
        # rook (8,0) attacks (8,x). King at (9,3). No.
        # rook (0,4) attacks (y,4). King at (9,3). No.
        
        # So King is safe.
        # Moves:
        # 1. (3,9)->(3,8): (3,8) is on Rank 8. Attacked by Rook at (8,0). -> Illegal.
        # 2. (3,9)->(4,9): (4,9) is on File 4. Attacked by Rook at (0,4). -> Illegal.
        
        moves = self.game.get_legal_moves()
        self.assertEqual(len(moves), 0, "Stalemate should have 0 legal moves")
        
        canonical_board = self.game.get_canonical_form(self.game.board, RED)
        result = self.game.get_game_ended(canonical_board, RED)
        self.assertEqual(result, -1, "Stalemate should be Loss (-1)")
        print("PASS: Stalemate detected as Loss.")

if __name__ == '__main__':
    unittest.main()
