import { BoardState, Color, PieceType, Position } from '../src/types';
import { getValidMoves, hasLegalMoves } from './gameLogic';

// --- Evaluation Constants ---

const PIECE_VALUES: Record<string, number> = {
  [PieceType.GENERAL]: 10000,
  [PieceType.CHARIOT]: 1000,
  [PieceType.CANNON]: 450,
  [PieceType.HORSE]: 400,
  [PieceType.ELEPHANT]: 20,
  [PieceType.ADVISOR]: 20,
  [PieceType.SOLDIER]: 10,
};

// Simplified position weights (just to encourage forward movement for soldiers/center control)
const getPositionBonus = (type: PieceType, color: Color, r: number, c: number): number => {
  // Flip row index for Red so calculations are symmetric
  // Logic assumes Black is at top (0-4), Red at bottom (5-9)
  const normalizedRow = color === Color.BLACK ? r : 9 - r;

  switch (type) {
    case PieceType.SOLDIER:
      // Bonus for crossing river (row > 4) and approaching palace
      if (normalizedRow > 4) return 20 + (normalizedRow - 4) * 10;
      return 0;
    case PieceType.CANNON:
      // Central column bonus
      if (c === 4) return 20;
      return 0;
    case PieceType.HORSE:
      // Penalty for being on edge
      if (c === 0 || c === 8) return -10;
      return 0;
    default:
      return 0;
  }
};

// --- Evaluation Function ---

const evaluateBoard = (board: BoardState, aiColor: Color): number => {
  let score = 0;
  const opponentColor = aiColor === Color.RED ? Color.BLACK : Color.RED;

  for (let r = 0; r < 10; r++) {
    for (let c = 0; c < 9; c++) {
      const piece = board[r][c];
      if (piece) {
        let value = PIECE_VALUES[piece.type] || 0;
        value += getPositionBonus(piece.type, piece.color, r, c);

        if (piece.color === aiColor) {
          score += value;
        } else {
          score -= value;
        }
      }
    }
  }
  return score;
};

// --- Minimax with Alpha-Beta Pruning ---

interface Move {
  from: Position;
  to: Position;
  score?: number;
}

const MAX_DEPTH = 3; // Depth 3 is reasonable for JS in browser without workers

export const getBestMove = (board: BoardState, turn: Color): Move | null => {
  // Initial call
  const [bestScore, bestMove] = minimax(board, MAX_DEPTH, -Infinity, Infinity, true, turn);
  return bestMove;
};

// Returns [score, move]
const minimax = (
  board: BoardState,
  depth: number,
  alpha: number,
  beta: number,
  isMaximizing: boolean,
  color: Color
): [number, Move | null] => {
  // 1. Base Case: Leaf node or Depth 0
  if (depth === 0) {
    // Evaluate from the perspective of the AI player (the one who called getBestMove)
    // We need to pass the original AI color down, or infer it. 
    // Here logic: if isMaximizing=true, it means it's 'color' turn. 
    // To simplify: evaluateBoard returns score relative to 'color' if isMaximizing started as true.

    // Actually, simple standard: Evaluation is always (AI Score - Opponent Score).
    // If isMaximizing, we want positive high. If minimizing, we want negative low.
    // The 'color' param passed here is the CURRENT turn player.
    // We need to know who the "Root" AI is.
    // Let's refactor slightly: Pass 'rootColor' or keep evaluating relative to current 'color'?
    // Standard Minimax: Eval function is static relative to Maximizer.
    const rootColor = isMaximizing ? color : (color === Color.RED ? Color.BLACK : Color.RED);
    return [evaluateBoard(board, rootColor), null];
  }

  // Check Game Over (No moves)
  if (!hasLegalMoves(board, color)) {
    // If current player has no moves, they lost.
    // If Maximizing player has no moves -> Score is -Infinity
    // If Minimizing player has no moves -> Score is +Infinity
    return [isMaximizing ? -100000 : 100000, null];
  }

  let bestMove: Move | null = null;

  // 2. Generate Moves
  // We collect all pieces of current color
  const allMoves: Move[] = [];
  for (let r = 0; r < 10; r++) {
    for (let c = 0; c < 9; c++) {
      const p = board[r][c];
      if (p && p.color === color) {
        const moves = getValidMoves(board, { row: r, col: c });
        for (const to of moves) {
          allMoves.push({ from: { row: r, col: c }, to });
        }
      }
    }
  }

  // Optimization: Sort moves? (Capture moves first usually helps alpha-beta)
  // Skipping for brevity, but recommended for deeper searches.

  if (isMaximizing) {
    let maxEval = -Infinity;
    for (const move of allMoves) {
      // Simulate Move
      const newBoard = board.map(row => row.map(p => p ? { ...p } : null));
      newBoard[move.to.row][move.to.col] = newBoard[move.from.row][move.from.col];
      newBoard[move.from.row][move.from.col] = null;

      const nextColor = color === Color.RED ? Color.BLACK : Color.RED;
      const [evalScore] = minimax(newBoard, depth - 1, alpha, beta, false, nextColor);

      if (evalScore > maxEval) {
        maxEval = evalScore;
        bestMove = move;
      }
      alpha = Math.max(alpha, evalScore);
      if (beta <= alpha) break; // Prune
    }
    return [maxEval, bestMove];
  } else {
    let minEval = Infinity;
    for (const move of allMoves) {
      // Simulate Move
      const newBoard = board.map(row => row.map(p => p ? { ...p } : null));
      newBoard[move.to.row][move.to.col] = newBoard[move.from.row][move.from.col];
      newBoard[move.from.row][move.from.col] = null;

      const nextColor = color === Color.RED ? Color.BLACK : Color.RED;
      const [evalScore] = minimax(newBoard, depth - 1, alpha, beta, true, nextColor);

      if (evalScore < minEval) {
        minEval = evalScore;
        bestMove = move;
      }
      beta = Math.min(beta, evalScore);
      if (beta <= alpha) break; // Prune
    }
    return [minEval, bestMove];
  }
};
