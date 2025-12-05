import { BoardState, Color, Piece, PieceType, Position } from '../types';

// Helper to check if pos is on board
const isValidPos = (r: number, c: number) => r >= 0 && r <= 9 && c >= 0 && c <= 8;

const isSameColor = (p1: Piece | null, color: Color) => p1 && p1.color === color;

// Check if move is basically valid (geometry & obstruction), WITHOUT checking for "Check"
// This is the "Physical" move validation.
const getPotentialMoves = (board: BoardState, pos: Position): Position[] => {
  const piece = board[pos.row][pos.col];
  if (!piece) return [];

  const moves: Position[] = [];
  const { row: r, col: c } = pos;
  const isRed = piece.color === Color.RED;

  // Helper to add move if target is empty or enemy
  const checkAdd = (nr: number, nc: number) => {
    if (!isValidPos(nr, nc)) return;
    const target = board[nr][nc];
    if (!target || target.color !== piece.color) {
      moves.push({ row: nr, col: nc });
    }
  };

  switch (piece.type) {
    case PieceType.GENERAL: {
      // Orthogonal 1 step, confined to palace
      // Palace Red: r 7-9, c 3-5
      // Palace Black: r 0-2, c 3-5
      const deltas = [[0, 1], [0, -1], [1, 0], [-1, 0]];
      deltas.forEach(([dr, dc]) => {
        const nr = r + dr;
        const nc = c + dc;
        if (nc < 3 || nc > 5) return;
        if (isRed) {
          if (nr < 7 || nr > 9) return;
        } else {
          if (nr < 0 || nr > 2) return;
        }
        checkAdd(nr, nc);
      });
      break;
    }
    case PieceType.ADVISOR: {
      // Diagonal 1 step, confined to palace
      const deltas = [[1, 1], [1, -1], [-1, 1], [-1, -1]];
      deltas.forEach(([dr, dc]) => {
        const nr = r + dr;
        const nc = c + dc;
        if (nc < 3 || nc > 5) return;
        if (isRed) {
          if (nr < 7 || nr > 9) return;
        } else {
          if (nr < 0 || nr > 2) return;
        }
        checkAdd(nr, nc);
      });
      break;
    }
    case PieceType.ELEPHANT: {
      // Diagonal 2 steps, cannot cross river, can be blocked ("eye")
      // Red side: r 5-9. Black side: r 0-4
      const deltas = [[2, 2], [2, -2], [-2, 2], [-2, -2]];
      deltas.forEach(([dr, dc]) => {
        const nr = r + dr;
        const nc = c + dc;
        if (isRed && nr < 5) return; // Crossing river
        if (!isRed && nr > 4) return; // Crossing river
        
        // Check "eye"
        const eyeR = r + dr / 2;
        const eyeC = c + dc / 2;
        if (isValidPos(eyeR, eyeC) && !board[eyeR][eyeC]) {
           checkAdd(nr, nc);
        }
      });
      break;
    }
    case PieceType.HORSE: {
      // L shape. Orthogonal 1 then Diagonal 1. Blockable if pivot is occupied.
      const movesData = [
        { dr: -2, dc: -1, legR: -1, legC: 0 },
        { dr: -2, dc: 1, legR: -1, legC: 0 },
        { dr: 2, dc: -1, legR: 1, legC: 0 },
        { dr: 2, dc: 1, legR: 1, legC: 0 },
        { dr: -1, dc: -2, legR: 0, legC: -1 },
        { dr: -1, dc: 2, legR: 0, legC: 1 },
        { dr: 1, dc: -2, legR: 0, legC: -1 },
        { dr: 1, dc: 2, legR: 0, legC: 1 },
      ];
      movesData.forEach(({ dr, dc, legR, legC }) => {
        const nr = r + dr;
        const nc = c + dc;
        const lr = r + legR;
        const lc = c + legC;
        if (isValidPos(lr, lc) && !board[lr][lc]) {
          checkAdd(nr, nc);
        }
      });
      break;
    }
    case PieceType.CHARIOT: {
      // Orthogonal any distance. Blocked by piece.
      const dirs = [[0, 1], [0, -1], [1, 0], [-1, 0]];
      dirs.forEach(([dr, dc]) => {
        let i = 1;
        while (true) {
          const nr = r + dr * i;
          const nc = c + dc * i;
          if (!isValidPos(nr, nc)) break;
          const target = board[nr][nc];
          if (!target) {
            moves.push({ row: nr, col: nc });
          } else {
            if (target.color !== piece.color) {
              moves.push({ row: nr, col: nc });
            }
            break; // Blocked
          }
          i++;
        }
      });
      break;
    }
    case PieceType.CANNON: {
      // Move like chariot, capture by jumping exactly one.
      const dirs = [[0, 1], [0, -1], [1, 0], [-1, 0]];
      dirs.forEach(([dr, dc]) => {
        let i = 1;
        let screenFound = false;
        while (true) {
          const nr = r + dr * i;
          const nc = c + dc * i;
          if (!isValidPos(nr, nc)) break;
          const target = board[nr][nc];
          if (!screenFound) {
            if (!target) {
              moves.push({ row: nr, col: nc });
            } else {
              screenFound = true; // Found the screen
            }
          } else {
            // After screen, looking for capture
            if (target) {
              if (target.color !== piece.color) {
                moves.push({ row: nr, col: nc });
              }
              break; // Cannot move past capture
            }
            // Cannot move to empty square after screen in Xiangqi? 
            // Correct: Cannons can only move to capture if jumping. 
            // If jumping over a piece to an empty spot, that's NOT allowed. 
            // Cannons move like rooks (if not capturing). 
            // If capturing, they must jump ONE piece.
          }
          i++;
        }
      });
      break;
    }
    case PieceType.SOLDIER: {
      // Forward 1. After river, Forward or Sideways 1. No backward.
      // Red direction: -1 (up). Black direction: +1 (down).
      const forward = isRed ? -1 : 1;
      const crossedRiver = isRed ? r <= 4 : r >= 5;
      
      // Forward
      checkAdd(r + forward, c);

      // Sideways
      if (crossedRiver) {
        checkAdd(r, c - 1);
        checkAdd(r, c + 1);
      }
      break;
    }
  }
  return moves;
};

// Check if Generals are facing each other with no pieces in between
const isFlyingGeneral = (board: BoardState): boolean => {
  let redGen: Position | null = null;
  let blackGen: Position | null = null;

  // Find generals
  for (let r = 0; r < 10; r++) {
    for (let c = 3; c < 6; c++) { // Generals always in col 3-5
      const p = board[r][c];
      if (p?.type === PieceType.GENERAL) {
        if (p.color === Color.RED) redGen = { row: r, col: c };
        else blackGen = { row: r, col: c };
      }
    }
  }

  if (!redGen || !blackGen) return false; // Should not happen in normal play
  if (redGen.col !== blackGen.col) return false;

  // Check pieces in between
  for (let r = blackGen.row + 1; r < redGen.row; r++) {
    if (board[r][redGen.col]) return false; // Found obstruction
  }
  return true; // Flying general condition met
};

// Check if `color` is currently in check
export const isCheck = (board: BoardState, color: Color): boolean => {
  // Find General
  let genPos: Position | null = null;
  for (let r = 0; r < 10; r++) {
    for (let c = 0; c < 9; c++) {
      const p = board[r][c];
      if (p && p.type === PieceType.GENERAL && p.color === color) {
        genPos = { row: r, col: c };
        break;
      }
    }
  }
  if (!genPos) return true; // Captured? (Shouldn't happen)

  // Check if any enemy piece attacks genPos
  // We can optimize by iterating all enemy pieces and seeing if genPos is in their potential moves
  // OR reverse check from General (e.g. is there a knight in knight-attacking spot?)
  // Iterating enemies is safer/easier to implement correctly.

  const enemyColor = color === Color.RED ? Color.BLACK : Color.RED;
  for (let r = 0; r < 10; r++) {
    for (let c = 0; c < 9; c++) {
      const p = board[r][c];
      if (p && p.color === enemyColor) {
        // We use getPotentialMoves directly.
        // Optimization: For cannon/chariot, we stop if we hit general.
        const moves = getPotentialMoves(board, { row: r, col: c });
        if (moves.some(m => m.row === genPos!.row && m.col === genPos!.col)) {
          return true;
        }
      }
    }
  }

  return false;
};

// Generate all fully legal moves (considering checks and flying general)
export const getValidMoves = (board: BoardState, pos: Position): Position[] => {
  const potential = getPotentialMoves(board, pos);
  const piece = board[pos.row][pos.col];
  if (!piece) return [];

  return potential.filter(move => {
    // Simulate move
    const newBoard = board.map(row => [...row]);
    newBoard[move.row][move.col] = newBoard[pos.row][pos.col];
    newBoard[pos.row][pos.col] = null;

    // 1. Check Flying General
    if (isFlyingGeneral(newBoard)) return false;

    // 2. Check if own General is under attack
    if (isCheck(newBoard, piece.color)) return false;

    return true;
  });
};

// Check for Checkmate or Stalemate
// If current player has NO valid moves, they lose.
export const hasLegalMoves = (board: BoardState, color: Color): boolean => {
  for (let r = 0; r < 10; r++) {
    for (let c = 0; c < 9; c++) {
      const p = board[r][c];
      if (p && p.color === color) {
        const moves = getValidMoves(board, { row: r, col: c });
        if (moves.length > 0) return true;
      }
    }
  }
  return false;
};
