import { BoardState, Color, PieceType } from './types';

// 10 rows (0-9), 9 cols (0-8)
// Row 0 is Black's back rank (Top)
// Row 9 is Red's back rank (Bottom)

export const INITIAL_BOARD: BoardState = [
  // Row 0 (Black Back)
  [
    { type: PieceType.CHARIOT, color: Color.BLACK },
    { type: PieceType.HORSE, color: Color.BLACK },
    { type: PieceType.ELEPHANT, color: Color.BLACK },
    { type: PieceType.ADVISOR, color: Color.BLACK },
    { type: PieceType.GENERAL, color: Color.BLACK },
    { type: PieceType.ADVISOR, color: Color.BLACK },
    { type: PieceType.ELEPHANT, color: Color.BLACK },
    { type: PieceType.HORSE, color: Color.BLACK },
    { type: PieceType.CHARIOT, color: Color.BLACK },
  ],
  // Row 1
  new Array(9).fill(null),
  // Row 2 (Black Cannons)
  [
    null,
    { type: PieceType.CANNON, color: Color.BLACK },
    null,
    null,
    null,
    null,
    null,
    { type: PieceType.CANNON, color: Color.BLACK },
    null,
  ],
  // Row 3 (Black Soldiers)
  [
    { type: PieceType.SOLDIER, color: Color.BLACK },
    null,
    { type: PieceType.SOLDIER, color: Color.BLACK },
    null,
    { type: PieceType.SOLDIER, color: Color.BLACK },
    null,
    { type: PieceType.SOLDIER, color: Color.BLACK },
    null,
    { type: PieceType.SOLDIER, color: Color.BLACK },
  ],
  // Row 4 (Empty - River side Black)
  new Array(9).fill(null),
  // Row 5 (Empty - River side Red)
  new Array(9).fill(null),
  // Row 6 (Red Soldiers)
  [
    { type: PieceType.SOLDIER, color: Color.RED },
    null,
    { type: PieceType.SOLDIER, color: Color.RED },
    null,
    { type: PieceType.SOLDIER, color: Color.RED },
    null,
    { type: PieceType.SOLDIER, color: Color.RED },
    null,
    { type: PieceType.SOLDIER, color: Color.RED },
  ],
  // Row 7 (Red Cannons)
  [
    null,
    { type: PieceType.CANNON, color: Color.RED },
    null,
    null,
    null,
    null,
    null,
    { type: PieceType.CANNON, color: Color.RED },
    null,
  ],
  // Row 8
  new Array(9).fill(null),
  // Row 9 (Red Back)
  [
    { type: PieceType.CHARIOT, color: Color.RED },
    { type: PieceType.HORSE, color: Color.RED },
    { type: PieceType.ELEPHANT, color: Color.RED },
    { type: PieceType.ADVISOR, color: Color.RED },
    { type: PieceType.GENERAL, color: Color.RED },
    { type: PieceType.ADVISOR, color: Color.RED },
    { type: PieceType.ELEPHANT, color: Color.RED },
    { type: PieceType.HORSE, color: Color.RED },
    { type: PieceType.CHARIOT, color: Color.RED },
  ],
];

export const PIECE_LABELS: Record<string, string> = {
  [`${Color.RED}-${PieceType.GENERAL}`]: '帥',
  [`${Color.RED}-${PieceType.ADVISOR}`]: '仕',
  [`${Color.RED}-${PieceType.ELEPHANT}`]: '相',
  [`${Color.RED}-${PieceType.HORSE}`]: '馬',
  [`${Color.RED}-${PieceType.CHARIOT}`]: '車',
  [`${Color.RED}-${PieceType.CANNON}`]: '炮',
  [`${Color.RED}-${PieceType.SOLDIER}`]: '兵',

  [`${Color.BLACK}-${PieceType.GENERAL}`]: '將',
  [`${Color.BLACK}-${PieceType.ADVISOR}`]: '士',
  [`${Color.BLACK}-${PieceType.ELEPHANT}`]: '象',
  [`${Color.BLACK}-${PieceType.HORSE}`]: '馬',
  [`${Color.BLACK}-${PieceType.CHARIOT}`]: '車',
  [`${Color.BLACK}-${PieceType.CANNON}`]: '砲',
  [`${Color.BLACK}-${PieceType.SOLDIER}`]: '卒',
};
