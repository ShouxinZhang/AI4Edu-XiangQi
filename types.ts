export enum Color {
  RED = 'red',
  BLACK = 'black',
}

export enum PieceType {
  GENERAL = 'general',
  ADVISOR = 'advisor',
  ELEPHANT = 'elephant',
  HORSE = 'horse',
  CHARIOT = 'chariot',
  CANNON = 'cannon',
  SOLDIER = 'soldier',
}

export enum GameMode {
  PVP = 'pvp', // Player vs Player
  PVE = 'pve', // Player vs Environment (AI)
  TRAINING = 'training',
}

export interface Position {
  row: number;
  col: number;
}

export interface Piece {
  type: PieceType;
  color: Color;
}

export type BoardState = (Piece | null)[][]; // 10 rows x 9 cols

export interface GameState {
  board: BoardState;
  turn: Color;
  selectedPos: Position | null;
  lastMove: { from: Position; to: Position } | null;
  winner: Color | null;
  inCheck: boolean;
  history: BoardState[]; // For undo
  gameMode: GameMode;
}