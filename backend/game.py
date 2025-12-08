
import numpy as np

# Board dimensions
BOARD_WIDTH = 9
BOARD_HEIGHT = 10

# Piece types
EMPTY = 0
KING = 1
ADVISOR = 2
ELEPHANT = 3
HORSE = 4
ROOK = 5
CANNON = 6
PAWN = 7

# Colors
RED = 1
BLACK = -1

class XiangqiGame:
    def __init__(self):
        self.board = self._init_board()
        self.current_player = RED
        self.move_history = []

    def _init_board(self):
        board = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=int)
        
        # Red pieces (positive) - BOTTOM (Rows 7-9)
        board[9][4] = KING
        board[9][3] = board[9][5] = ADVISOR
        board[9][2] = board[9][6] = ELEPHANT
        board[9][1] = board[9][7] = HORSE
        board[9][0] = board[9][8] = ROOK
        board[7][1] = board[7][7] = CANNON
        board[6][0] = board[6][2] = board[6][4] = board[6][6] = board[6][8] = PAWN

        # Black pieces (negative) - TOP (Rows 0-2)
        board[0][4] = -KING
        board[0][3] = board[0][5] = -ADVISOR
        board[0][2] = board[0][6] = -ELEPHANT
        board[0][1] = board[0][7] = -HORSE
        board[0][0] = board[0][8] = -ROOK
        board[2][1] = board[2][7] = -CANNON
        board[3][0] = board[3][2] = board[3][4] = board[3][6] = board[3][8] = -PAWN
        
        return board

    def get_init_board(self):
        return self._init_board()

    def get_legal_moves(self):
        # Generate pseudo-legal moves first
        pseudo_moves = self._get_pseudo_legal_moves()
        
        # Filter moves that leave King in check (Suicide)
        # and moves that violate Flying General rule
        valid_moves = []
        for move in pseudo_moves:
            if self._is_move_safe(move):
                valid_moves.append(move)
        
        return valid_moves

    def _get_pseudo_legal_moves(self):
        # Implementation of geometric moves generation (renamed from get_legal_moves)
        moves = []
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                piece = self.board[y][x]
                if piece * self.current_player > 0:
                    moves.extend(self._get_moves_for_piece(x, y, piece))
        return moves

    def _get_king_pos(self, player):
        target = KING if player == RED else -KING
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x] == target:
                    return (x, y)
        return None

    def is_in_check(self, player):
        # Find King
        king_pos = self._get_king_pos(player)
        if not king_pos:
            return True # King captured = Check (technically lost)
            
        # Check against all enemy pieces
        enemy = -player
        
        # SAVE STATE: Move generation relies on self.current_player
        # We need to see if ENEMY pieces can attack King.
        # So we must pretend it is ENEMY's turn to generate their moves correctly.
        original_player = self.current_player
        self.current_player = enemy
        
        try:
            for y in range(BOARD_HEIGHT):
                for x in range(BOARD_WIDTH):
                    piece = self.board[y][x]
                    if piece * enemy > 0:
                        # Generate moves for this enemy piece
                        moves = self._get_moves_for_piece(x, y, piece)
                        if (king_pos[0], king_pos[1]) in [m[1] for m in moves]:
                            return True
        finally:
            # RESTORE STATE
            self.current_player = original_player
            
        return False

    def _is_move_safe(self, move):
        start, end = move
        
        # 1. Apply move to a temp board
        original_piece = self.board[end[1]][end[0]]
        self.board[end[1]][end[0]] = self.board[start[1]][start[0]]
        self.board[start[1]][start[0]] = 0
        
        # 2. Check if self is in check
        in_check = self.is_in_check(self.current_player)
        
        # 3. Check for Flying General (Kings facing each other)
        if not in_check:
            in_check = self._is_flying_general()

        # 4. Revert move
        self.board[start[1]][start[0]] = self.board[end[1]][end[0]]
        self.board[end[1]][end[0]] = original_piece
        
        return not in_check

    def _is_flying_general(self):
        # Check if Kings are on same column with no pieces in between
        red_king = self._get_king_pos(RED)
        black_king = self._get_king_pos(BLACK)
        
        if not red_king or not black_king:
            return False
            
        if red_king[0] != black_king[0]:
            return False # Not on same column
            
        # Check intervening pieces
        min_y = min(red_king[1], black_king[1])
        max_y = max(red_king[1], black_king[1])
        
        for y in range(min_y + 1, max_y):
            if self.board[y][red_king[0]] != 0:
                return False # There is an obstacle
                
        return True # No obstacles = Flying General!

    def _get_moves_for_piece(self, x, y, piece):
        piece_type = abs(piece)
        if piece_type == KING:
            return self._get_king_moves(x, y)
        elif piece_type == ADVISOR:
            return self._get_advisor_moves(x, y)
        elif piece_type == ELEPHANT:
            return self._get_elephant_moves(x, y)
        elif piece_type == HORSE:
            return self._get_horse_moves(x, y)
        elif piece_type == ROOK:
            return self._get_rook_moves(x, y)
        elif piece_type == CANNON:
            return self._get_cannon_moves(x, y)
        elif piece_type == PAWN:
            return self._get_pawn_moves(x, y)
        return []

    def _is_valid(self, x, y):
        return 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT

    def _is_enemy(self, x, y, player):
        # player is 1 (Red) or -1 (Black)
        # return True if board[y][x] is occupied by enemy
        piece = self.board[y][x]
        return piece != 0 and (piece * player < 0)

    def _is_empty(self, x, y):
        return self.board[y][x] == 0

    def _is_own(self, x, y, player):
        piece = self.board[y][x]
        return piece != 0 and (piece * player > 0)

    def _get_king_moves(self, x, y):
        moves = []
        # King moves: orthogonal 1 step, confined to palace
        # Palace x: 3-5
        # Palace y: 0-2 (Red), 7-9 (Black)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        player = self.current_player
        
        # Palace bounds
        min_x, max_x = 3, 5
        min_y, max_y = (7, 9) if player == RED else (0, 2)  # Red at bottom, Black at top

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if min_x <= nx <= max_x and min_y <= ny <= max_y:
                if not self._is_own(nx, ny, player):
                    moves.append(((x, y), (nx, ny)))
        return moves

    def _get_advisor_moves(self, x, y):
        moves = []
        # Advisor moves: diagonal 1 step, confined to palace
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        player = self.current_player
        
        min_x, max_x = 3, 5
        min_y, max_y = (7, 9) if player == RED else (0, 2)  # Red at bottom, Black at top

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if min_x <= nx <= max_x and min_y <= ny <= max_y:
                if not self._is_own(nx, ny, player):
                    moves.append(((x, y), (nx, ny)))
        return moves

    def _get_elephant_moves(self, x, y):
        moves = []
        # Elephant moves: diagonal 2 steps, cannot cross river, blocking eye
        directions = [(2, 2), (2, -2), (-2, 2), (-2, -2)]
        eyes = [(1, 1), (1, -1), (-1, 1), (-1, -1)] # Relative eye positions
        player = self.current_player
        
        # River boundary behavior: Red (y<=4), Black (y>=5)
        # Valid y for Red Elephants: 0, 2, 4
        # Valid y for Black Elephants: 5, 7, 9
        # Simplified: Check if crossing river
        
        for i, (dx, dy) in enumerate(directions):
            nx, ny = x + dx, y + dy
            eye_x, eye_y = x + eyes[i][0], y + eyes[i][1]

            if self._is_valid(nx, ny):
                # Check river crossing
                # Red (Bottom) cannot enter Top (0-4)
                if player == RED and ny < 5: continue
                # Black (Top) cannot enter Bottom (5-9)
                if player == BLACK and ny > 4: continue
                
                # Check blocking eye
                if self._is_empty(eye_x, eye_y):
                    if not self._is_own(nx, ny, player):
                        moves.append(((x, y), (nx, ny)))
        return moves

    def _get_horse_moves(self, x, y):
        moves = []
        # Horse moves: "Sun" shape, sensitive to "blocking leg"
        # Legs: orthogonal 1 step
        # Moves: orthogonal 1 step then diagonal 1 step
        knight_moves = [
            (1, 2), (1, -2), (-1, 2), (-1, -2),
            (2, 1), (2, -1), (-2, 1), (-2, -1)
        ]
        # Corresponding legs (dx, dy) to check
        legs = [
            (0, 1), (0, -1), (0, 1), (0, -1),
            (1, 0), (1, 0), (-1, 0), (-1, 0)
        ]
        
        player = self.current_player
        for i, (dx, dy) in enumerate(knight_moves):
            nx, ny = x + dx, y + dy
            leg_x, leg_y = x + legs[i][0], y + legs[i][1]
            
            if self._is_valid(nx, ny):
                if self._is_empty(leg_x, leg_y): # Check leg
                    if not self._is_own(nx, ny, player):
                        moves.append(((x, y), (nx, ny)))
        return moves

    def _get_rook_moves(self, x, y):
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        player = self.current_player
        
        for dx, dy in directions:
            cur_x, cur_y = x + dx, y + dy
            while self._is_valid(cur_x, cur_y):
                if self._is_empty(cur_x, cur_y):
                    moves.append(((x, y), (cur_x, cur_y)))
                else:
                    if self._is_enemy(cur_x, cur_y, player):
                        moves.append(((x, y), (cur_x, cur_y)))
                    break
                cur_x += dx
                cur_y += dy
        return moves

    def _get_cannon_moves(self, x, y):
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        player = self.current_player
        
        for dx, dy in directions:
            cur_x, cur_y = x + dx, y + dy
            platform_found = False
            while self._is_valid(cur_x, cur_y):
                if not platform_found:
                    if self._is_empty(cur_x, cur_y):
                        moves.append(((x, y), (cur_x, cur_y)))
                    else:
                        platform_found = True # Found the platform (friend or foe)
                else:
                    # After platform, looking for enemy to capture
                    if not self._is_empty(cur_x, cur_y):
                        if self._is_enemy(cur_x, cur_y, player):
                            moves.append(((x, y), (cur_x, cur_y)))
                        break # Cannot jump over two pieces
                cur_x += dx
                cur_y += dy
        return moves

    def _get_pawn_moves(self, x, y):
        moves = []
        player = self.current_player
        # Red moves -1 y (Up), Black moves +1 y (Down)
        dy = -1 if player == RED else 1
        
        # Forward move
        nx, ny = x, y + dy
        if self._is_valid(nx, ny) and not self._is_own(nx, ny, player):
            moves.append(((x, y), (nx, ny)))
            
        # Horizontal moves if crossed river
        # Red river: y < 5 (into top half)
        # Black river: y > 4 (into bottom half)
        crossed_river = (player == RED and y < 5) or (player == BLACK and y > 4)
        if crossed_river:
            for dx in [-1, 1]:
                nx, ny = x + dx, y
                if self._is_valid(nx, ny) and not self._is_own(nx, ny, player):
                    moves.append(((x, y), (nx, ny)))
                    
        return moves

    def make_move(self, move):
        # move is tuple ((x1, y1), (x2, y2))
        start, end = move
        self.board[end[1]][end[0]] = self.board[start[1]][start[0]]
        self.board[start[1]][start[0]] = EMPTY
        self.current_player *= -1
        self.move_history.append(move)

    def is_game_over(self):
        # Simple check: is King captured?
        kings = np.where(np.abs(self.board) == KING)
        if len(kings[0]) < 2:
            return True
        return False
    
    def get_winner(self):
        if not self.is_game_over():
            return 0
        
        # Check which king remains
        kings = np.where(self.board == KING) # Red King
        if len(kings[0]) == 0: return -1 # Black wins
        
        kings = np.where(self.board == -KING) # Black King
        if len(kings[0]) == 0: return 1 # Red wins
        
        return 0

    def get_canonical_board(self):
        # Return board from current player's perspective
        # If Black (player -1), flip the board and negate pieces
        # Flipping means x -> x, y -> 9-y
        if self.current_player == 1:
            return self.board
        else:
            return np.flipud(self.board) * -1

    def to_tensor(self):
        return self.state_to_tensor(self.get_canonical_board())

    def state_to_tensor(self, board):
        # Neural network input: 9x10 x 14 channels
        state = np.zeros((14, BOARD_HEIGHT, BOARD_WIDTH), dtype=np.float32)
        
        # Channels 0-6: Own pieces
        # Channels 7-13: Enemy pieces
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                p = board[y][x]
                if p != 0:
                    # p > 0 is own (since canonical), p < 0 is enemy
                    piece_type = abs(p) - 1 # 0-6
                    if p > 0:
                        state[piece_type][y][x] = 1.0
                    else:
                        state[piece_type + 7][y][x] = 1.0
        return state

    def encode_move(self, move):
        # move: ((x1, y1), (x2, y2))
        # 0 <= x < 9, 0 <= y < 10
        # linear index = y * 9 + x
        # action = start_idx * 90 + end_idx
        start, end = move
        
        # If current player is Black, we need to flip coordinates for canonical encoding
        # But wait, usually we encode moves in absolute coordinates for the game
        # and flip them only when passing to/from network?
        # Let's keep one standard: Absolute Board Coordinates.
        # The network will learn to output absolute coordinates relative to the input board orientation.
        
        # However, to reuse the network for both colors, we usually feed "canonical board" 
        # (where self is always at bottom/top).
        # If we use canonical board, we must flip moves too.
        
        # Let's stick to:
        # Game logic uses Absolute Coordinates (Red at top y=0, Black at bottom y=9).
        # We also need a handle to convert "Network Action" back to "Absolute Move".
        
        p1 = start[1] * 9 + start[0]
        p2 = end[1] * 9 + end[0]
        return p1 * 90 + p2

    def decode_move(self, action_idx):
        p1 = action_idx // 90
        p2 = action_idx % 90
        
        x1, y1 = p1 % 9, p1 // 9
        x2, y2 = p2 % 9, p2 // 9
        return ((x1, y1), (x2, y2))

    # MCTS Compatibility Methods
    
    def get_board_size(self):
        return (BOARD_HEIGHT, BOARD_WIDTH)

    def get_action_size(self):
        return 8100

    def get_next_state(self, board, player, action):
        """
        Return the next board state and player.
        IMPORTANT: This method must accept an Absolute Board and return an Absolute Board.
        The action is derived from MCTS which uses Canonical Board, so the action
        coordinates are in Canonical space. We must convert them if necessary.
        """
        move_canonical = self.decode_move(action)
        start_c, end_c = move_canonical
        
        # Convert Canonical Coordinates to Absolute Coordinates
        if player == 1:
            # Red: Canonical is same as Absolute
            start_a, end_a = start_c, end_c
        else:
            # Black: Canonical is flipped. We must flip back to Absolute.
            # y -> 9 - y
            start_a = (start_c[0], 9 - start_c[1])
            end_a = (end_c[0], 9 - end_c[1])
            
        next_board = np.copy(board)
        
        # Apply move in Absolute Coordinates
        # (Coordinate format is (x,y), board access is [y][x])
        next_board[end_a[1]][end_a[0]] = next_board[start_a[1]][start_a[0]]
        next_board[start_a[1]][start_a[0]] = 0
        
        return next_board, -player

    def get_valid_moves(self, board, player):
        # return fixed size binary vector
        valids = [0] * self.get_action_size()
        
        # Reconstruct game state
        # board is canonical. Pretend we are Red (1).
        temp_game = XiangqiGame()
        temp_game.board = np.copy(board)
        temp_game.current_player = 1 # Always 1 for canonical
        
        legal_moves = temp_game.get_legal_moves()
        
        for move in legal_moves:
            idx = self.encode_move(move)
            if idx < 8100:
                valids[idx] = 1
                
        return np.array(valids)

    def get_game_ended(self, board, player):
        # board is canonical.
        # return 0 if not ended, 1 if player wins, -1 if player lost, 1e-4 if draw
        
        # 1. Check for King capture (Optimization: if King is gone, it's definitely a loss)
        kings = np.where(board == KING)
        if len(kings[0]) == 0: return -1 # Player lost (King missing)
        
        enemy_kings = np.where(board == -KING)
        if len(enemy_kings[0]) == 0: return 1 # Player won (Enemy King captured)
        
        # 2. Check for Checkmate / Stalemate (困毙) -> Loss in Xiangqi
        # We need to check if current player has any legal moves.
        # get_valid_moves constructs a temp game and calls get_legal_moves (which now checks for safety)
        valids = self.get_valid_moves(board, player)
        if np.sum(valids) == 0:
            return -1 # Loss (No legal moves left)
            
        return 0

    def get_canonical_form(self, board, player):
        if player == 1:
            return board
        else:
            return np.flipud(board) * -1

    def string_representation(self, board):
        return board.tobytes()


