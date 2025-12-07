"""
Classic Board Evaluation.

Contains heuristic evaluation functions and piece values.
Enhanced with Piece-Square Tables (PST) based on standard Xiangqi strategy.
Values are relative to Red (Top, y=0) perspective.
"""

# Base Piece values
PIECE_VALUES = {
    1: 10000,  # KING
    2: 20,     # ADVISOR
    3: 20,     # ELEPHANT
    4: 45,     # HORSE
    5: 90,     # ROOK
    6: 50,     # CANNON
    7: 10,     # PAWN
}

# -----------------------------------------------------------------------------
# Piece-Square Tables (Red Perspective: y=0 Top -> y=9 Bottom)
# -----------------------------------------------------------------------------

# PAWN: Crossing river (y>4) is key. Approaching palace (y=7,8) is best.
PAWN_PST = [
    [0,  0,  0,  0,  0,  0,  0,  0,  0], # y=0
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  0,  0,  0,  0,  0], # y=3 (Initial)
    [0,  2,  0,  2,  0,  2,  0,  2,  0], # y=4 (River bank)
    [10, 20, 20, 20, 20, 20, 20, 20, 10], # y=5 (Crossed)
    [20, 30, 40, 50, 60, 50, 40, 30, 20], # y=6
    [20, 30, 40, 50, 60, 50, 40, 30, 20], # y=7
    [10, 20, 30, 30, 30, 30, 30, 20, 10], # y=8
    [0,  10, 20, 20, 20, 20, 20, 10, 0],  # y=9 (Bottom)
]

# ROOK: Value mobility and key lines.
ROOK_PST = [
    [-5,  0,  0,  0,  0,  0,  0,  0, -5], # y=0
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
    [5,   5,  5,  5,  5,  5,  5,  5,  5], # y=4 River
    [5,   5,  5,  5,  5,  5,  5,  5,  5], # y=5 River
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
    [0,   0,  0,  5,  5,  5,  0,  0,  0],
    [-5,  0,  0,  5,  5,  5,  0,  0, -5], # y=9
]

# HORSE: Center is good, corners bad.
HORSE_PST = [
    [-5, -5, -5, -5, -5, -5, -5, -5, -5], # y=0
    [-5,  0,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  5,  5,  5,  5,  5,  0, -5],
    [-5,  5, 10, 15, 15, 15, 10,  5, -5], # y=3
    [-5,  5, 10, 15, 15, 15, 10,  5, -5], # y=4
    [-5,  5, 12, 18, 18, 18, 12,  5, -5], # y=5
    [-5,  5, 10, 15, 15, 15, 10,  5, -5],
    [-5,  5,  5,  8,  8,  8,  5,  5, -5],
    [-5,  0,  3,  5,  5,  5,  3,  0, -5],
    [-5, -5, -5, -5, -5, -5, -5, -5, -5],
]

# CANNON: Mounts (y=2, x=1,7) are good. Central files good.
CANNON_PST = [
    [0,   0,  1,  3,  3,  3,  1,  0,  0], # y=0
    [0,   1,  1,  2,  2,  2,  1,  1,  0],
    [3,   3,  5,  5,  8,  5,  5,  3,  3], # y=2 (Home row for cannons)
    [0,   1,  2,  3,  5,  3,  2,  1,  0],
    [0,   1,  5,  5,  5,  5,  5,  1,  0],
    [0,   1,  5,  5,  5,  5,  5,  1,  0],
    [0,   1,  2,  3,  3,  3,  2,  1,  0],
    [1,   1,  1,  1,  1,  1,  1,  1,  1],
    [2,   2,  2,  2,  2,  2,  2,  2,  2], # y=8
    [0,   0,  0,  0,  0,  0,  0,  0,  0],
]

# ELEPHANT: Defensive, stay home (y0,2,4).
ELEPHANT_PST = [
    [0,  0,  1,  0,  0,  0,  1,  0,  0], # y=0
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  0,  0,  3,  0,  0,  0,  0], # y=2 (Center)
    [0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0,  0,  1,  0,  0,  0,  1,  0,  0], # y=4
    [0] * 9, # y=5 (Cannot cross)
    [0] * 9,
    [0] * 9,
    [0] * 9,
    [0] * 9,
]

# ADVISOR: Defensive in palace (y0-2, x3-5).
ADVISOR_PST = [
    [0,  0,  0,  1,  3,  1,  0,  0,  0], # y=0
    [0,  0,  0,  0,  3,  0,  0,  0,  0], # y=1
    [0,  0,  0,  1,  3,  1,  0,  0,  0], # y=2
    [0] * 9,
    [0] * 9,
    [0] * 9,
    [0] * 9,
    [0] * 9,
    [0] * 9,
    [0] * 9,
]

# KING: Survival.
KING_PST = [
    [0,  0,  0,  1,  1,  1,  0,  0,  0], # y=0
    [0,  0,  0,  2,  5,  2,  0,  0,  0], # y=1 Center is safest
    [0,  0,  0,  1,  1,  1,  0,  0,  0], # y=2
    [0] * 9,
    [0] * 9,
    [0] * 9,
    [0] * 9,
    [0] * 9,
    [0] * 9,
    [0] * 9,
]

def evaluate_board(board) -> float:
    """
    Evaluation function with Material + Position Bonus.
    
    Args:
        board: 10x9 numpy array (Red positive, Black negative)
        
    Returns:
        Score (Red perspective)
    """
    score = 0
    
    # Pre-fetch lookup tables to avoid lookups in inner loop
    pst_map = {
        1: KING_PST,
        2: ADVISOR_PST,
        3: ELEPHANT_PST,
        4: HORSE_PST,
        5: ROOK_PST,
        6: CANNON_PST,
        7: PAWN_PST
    }

    for y in range(10):
        for x in range(9):
            piece = board[y][x]
            if piece == 0:
                continue
            
            p_type = abs(piece)
            base_val = PIECE_VALUES.get(p_type, 0)
            
            # Position Bonus
            pst = pst_map.get(p_type)
            if not pst:
                continue

            if piece > 0: # RED
                pst_val = pst[y][x]
                score += (base_val + pst_val)
                
            else: # BLACK
                # Mirror coordinates for Black (y' = 9-y)
                # Note: Xiangqi boards is symmetric horizontally for strategy usually,
                # but let's stick to simple vertical mirror.
                # Actually, Black Pawn at y=6 (Red side) is like Red Pawn at y=3 (Black side).
                # Wait.
                # Red Pawn at y=3 (Start).
                # Black Pawn at y=6 (Start).
                # PST[3] for Red is Initial.
                # For Black at y=6, 9-6=3. So matches PST[3]. Correct.
                
                mirror_y = 9 - y
                pst_val = pst[mirror_y][x]
                score -= (base_val + pst_val)
                
    return score
