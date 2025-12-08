/**
 * Game State Management using React Context + useReducer
 */
import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { BoardState, Color, GameMode, Position, GameState } from '../types';
import { INITIAL_BOARD } from '../constants';
import { cloneBoard } from '../utils/gameLogic';

// Action types
type GameAction =
    | { type: 'SELECT_PIECE'; position: Position }
    | { type: 'MAKE_MOVE'; from: Position; to: Position; newBoard: BoardState }
    | { type: 'SET_WINNER'; winner: Color | null }
    | { type: 'SET_CHECK'; inCheck: boolean }
    | { type: 'UNDO' }
    | { type: 'RESET' }
    | { type: 'SET_MODE'; mode: GameMode }
    | { type: 'SET_BOARD'; board: BoardState; turn?: Color }
    | { type: 'SET_DIFFICULTY'; difficulty: number };

// Initial state
const initialState: GameState = {
    board: cloneBoard(INITIAL_BOARD),
    turn: Color.RED,
    selectedPos: null,
    lastMove: null,
    winner: null,
    inCheck: false,
    history: [],
    moveHistory: [],
    gameMode: GameMode.PVP,
    difficulty: 2, // Default Level 2
};

// Reducer
function gameReducer(state: GameState, action: GameAction): GameState {
    switch (action.type) {
        case 'SELECT_PIECE':
            return { ...state, selectedPos: action.position };

        case 'MAKE_MOVE':
            return {
                ...state,
                board: action.newBoard,
                turn: state.turn === Color.RED ? Color.BLACK : Color.RED,
                selectedPos: null,
                lastMove: { from: action.from, to: action.to },
                history: [...state.history, state.board],
                moveHistory: [...state.moveHistory, { from: action.from, to: action.to }],
            };

        case 'SET_WINNER':
            return { ...state, winner: action.winner };

        case 'SET_CHECK':
            return { ...state, inCheck: action.inCheck };

        case 'UNDO':
            if (state.history.length === 0) return state;
            const prevBoard = state.history[state.history.length - 1];
            return {
                ...state,
                board: prevBoard,
                turn: state.turn === Color.RED ? Color.BLACK : Color.RED,
                selectedPos: null,
                lastMove: null,
                winner: null,
                history: state.history.slice(0, -1),
            };

        case 'RESET':
            return {
                ...initialState,
                gameMode: state.gameMode,
                difficulty: state.difficulty,
            };

        case 'SET_MODE':
            return {
                ...initialState,
                gameMode: action.mode,
            };

        case 'SET_BOARD':
            return {
                ...state,
                board: action.board,
                turn: action.turn ?? state.turn,
            };

        case 'SET_DIFFICULTY':
            return {
                ...state,
                difficulty: action.difficulty,
            };

        default:
            return state;
    }
}

// Context
interface GameContextType {
    state: GameState;
    dispatch: React.Dispatch<GameAction>;
    // Helper actions
    selectPiece: (pos: Position) => void;
    makeMove: (from: Position, to: Position, newBoard: BoardState) => void;
    setWinner: (winner: Color | null) => void;
    undo: () => void;
    reset: () => void;
    setMode: (mode: GameMode) => void;
    setBoard: (board: BoardState, turn?: Color) => void;
    setDifficulty: (level: number) => void;
}

const GameContext = createContext<GameContextType | undefined>(undefined);

// Provider component
export function GameProvider({ children }: { children: ReactNode }) {
    const [state, dispatch] = useReducer(gameReducer, initialState);

    const value: GameContextType = {
        state,
        dispatch,
        selectPiece: (pos) => dispatch({ type: 'SELECT_PIECE', position: pos }),
        makeMove: (from, to, newBoard) => dispatch({ type: 'MAKE_MOVE', from, to, newBoard }),
        setWinner: (winner) => dispatch({ type: 'SET_WINNER', winner }),
        undo: () => dispatch({ type: 'UNDO' }),
        reset: () => dispatch({ type: 'RESET' }),
        setMode: (mode) => dispatch({ type: 'SET_MODE', mode }),
        setBoard: (board, turn) => dispatch({ type: 'SET_BOARD', board, turn }),
        setDifficulty: (level) => dispatch({ type: 'SET_DIFFICULTY', difficulty: level }),
    };

    return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
}

// Hook to use game context
export function useGame() {
    const context = useContext(GameContext);
    if (context === undefined) {
        throw new Error('useGame must be used within a GameProvider');
    }
    return context;
}

export { GameContext };
