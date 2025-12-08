/**
 * Replay Store - Manages game replay state
 */
import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { BoardState, Position } from '../types';
import { INITIAL_BOARD } from '../constants';
import { cloneBoard } from '../utils/gameLogic';

interface ReplayMove {
    from: Position;
    to: Position;
}

interface ReplayState {
    gameId: string | null;
    moves: ReplayMove[];
    currentStep: number;
    boards: BoardState[];  // Pre-computed boards at each step
    isLoading: boolean;
    error: string | null;
}

type ReplayAction =
    | { type: 'LOAD_START' }
    | { type: 'LOAD_SUCCESS'; gameId: string; moves: ReplayMove[]; boards: BoardState[] }
    | { type: 'LOAD_ERROR'; error: string }
    | { type: 'GO_TO_STEP'; step: number }
    | { type: 'NEXT_STEP' }
    | { type: 'PREV_STEP' }
    | { type: 'RESET' };

const initialState: ReplayState = {
    gameId: null,
    moves: [],
    currentStep: 0,
    boards: [cloneBoard(INITIAL_BOARD)],
    isLoading: false,
    error: null,
};

function replayReducer(state: ReplayState, action: ReplayAction): ReplayState {
    switch (action.type) {
        case 'LOAD_START':
            return { ...state, isLoading: true, error: null };

        case 'LOAD_SUCCESS':
            return {
                ...state,
                isLoading: false,
                gameId: action.gameId,
                moves: action.moves,
                boards: action.boards,
                currentStep: 0,
            };

        case 'LOAD_ERROR':
            return { ...state, isLoading: false, error: action.error };

        case 'GO_TO_STEP':
            return {
                ...state,
                currentStep: Math.max(0, Math.min(action.step, state.boards.length - 1)),
            };

        case 'NEXT_STEP':
            return {
                ...state,
                currentStep: Math.min(state.currentStep + 1, state.boards.length - 1),
            };

        case 'PREV_STEP':
            return {
                ...state,
                currentStep: Math.max(state.currentStep - 1, 0),
            };

        case 'RESET':
            return initialState;

        default:
            return state;
    }
}

// Helper: Apply a move to a board and return new board
function applyMove(board: BoardState, from: Position, to: Position): BoardState {
    const newBoard = board.map(row => row.map(p => p ? { ...p } : null)) as BoardState;
    newBoard[to.row][to.col] = newBoard[from.row][from.col];
    newBoard[from.row][from.col] = null;
    return newBoard;
}

// Helper: Reconstruct all boards from moves
function reconstructBoards(moves: ReplayMove[]): BoardState[] {
    const boards: BoardState[] = [cloneBoard(INITIAL_BOARD)];
    let current = boards[0];

    for (const move of moves) {
        current = applyMove(current, move.from, move.to);
        boards.push(current);
    }

    return boards;
}

interface ReplayContextType {
    state: ReplayState;
    dispatch: React.Dispatch<ReplayAction>;
    loadGame: (gameId: string) => Promise<void>;
    loadGameFromData: (gameId: string, rawMoves: number[][][]) => void;
    nextStep: () => void;
    prevStep: () => void;
    goToStep: (step: number) => void;
    reset: () => void;
}

const ReplayContext = createContext<ReplayContextType | undefined>(undefined);

export function ReplayProvider({ children }: { children: ReactNode }) {
    const [state, dispatch] = useReducer(replayReducer, initialState);

    const loadGame = async (gameId: string) => {
        dispatch({ type: 'LOAD_START' });
        try {
            // This would call API if we had individual game endpoints
            dispatch({ type: 'LOAD_ERROR', error: 'Use loadGameFromData instead' });
        } catch (e: any) {
            dispatch({ type: 'LOAD_ERROR', error: e.message });
        }
    };

    // Load game directly from data (called by ReplayPage with game data)
    const loadGameFromData = (gameId: string, rawMoves: number[][][]) => {
        dispatch({ type: 'LOAD_START' });
        try {
            console.log('[Replay] Raw moves:', rawMoves);
            // Convert raw moves [[from, to], ...] to ReplayMove[]
            // Raw format: [[[col, row], [col, row]], ...]
            const moves: ReplayMove[] = rawMoves.map(move => ({
                from: { row: move[0][1], col: move[0][0] },
                to: { row: move[1][1], col: move[1][0] }
            }));
            console.log('[Replay] Parsed moves:', moves);

            const boards = reconstructBoards(moves);
            console.log('[Replay] Reconstructed boards count:', boards.length);

            // Debug Move 4 (Index 4 in boards array, after move 4 applied)
            if (boards.length > 4) {
                console.log('[Replay] Board[4] (After Move 4) at (7,9) [row 9, col 7]:', boards[4][9][7]);
                console.log('[Replay] Board[3] (Before Move 4) at (7,2) [row 2, col 7]:', boards[3][2][7]);
                console.log('[Replay] Move 4 details:', moves[3]);
            }

            dispatch({ type: 'LOAD_SUCCESS', gameId, moves, boards });
        } catch (e: any) {
            dispatch({ type: 'LOAD_ERROR', error: e.message || 'Failed to load game' });
        }
    };

    const value: ReplayContextType = {
        state,
        dispatch,
        loadGame,
        loadGameFromData,
        nextStep: () => dispatch({ type: 'NEXT_STEP' }),
        prevStep: () => dispatch({ type: 'PREV_STEP' }),
        goToStep: (step) => dispatch({ type: 'GO_TO_STEP', step }),
        reset: () => dispatch({ type: 'RESET' }),
    };

    return <ReplayContext.Provider value={value}>{children}</ReplayContext.Provider>;
}

export function useReplay() {
    const context = useContext(ReplayContext);
    if (context === undefined) {
        throw new Error('useReplay must be used within a ReplayProvider');
    }
    return context;
}

export { ReplayContext };

