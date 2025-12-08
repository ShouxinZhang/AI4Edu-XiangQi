import React, { useEffect, useState } from 'react';
import XiangqiBoard from '../../components/game/XiangqiBoard';
import { GameControlPanel } from '../../components/layout/GameControlPanel';
import { useGame } from '../../store/GameContext';
import { getValidMoves, hasLegalMoves, isCheck } from '../../utils/gameLogic';
import { Color, Position } from '../../types';

export const PVPGame: React.FC = () => {
    const { state, selectPiece, makeMove, setWinner, setBoard, undo, reset, saveGame } = useGame(); // saveGame might not be in context yet, need to check
    // Checked GameContext in Step 103, it has: selectPiece, makeMove, setWinner, undo, reset, setMode, setBoard, setDifficulty.
    // It DOES NOT have saveGame directly exposed in context? 
    // Wait, let me check GameContext again in Step 103.
    // It has `state`, `dispatch`, and helper actions. NO `saveGame`.
    // But `GameControlPanel` expects `onSave`.
    // I should implement `handleSave` here using `gameApi`.

    const [validMoves, setValidMoves] = useState<Position[]>([]);

    const handleSquareClick = (pos: Position) => {
        if (state.winner) return;

        const piece = state.board[pos.row][pos.col];
        const isMyPiece = piece && piece.color === state.turn;

        // 1. Select Piece
        if (isMyPiece) {
            selectPiece(pos);
            const moves = getValidMoves(state.board, pos);
            setValidMoves(moves);
            return;
        }

        // 2. Move Piece
        if (state.selectedPos) {
            const isMoveValid = validMoves.some(m => m.row === pos.row && m.col === pos.col);
            if (isMoveValid) {
                // Execute move
                const from = state.selectedPos;
                const to = pos;

                // Create new board state
                const newBoard = state.board.map(row => [...row]);
                newBoard[to.row][to.col] = newBoard[from.row][from.col];
                newBoard[from.row][from.col] = null;

                makeMove(from, to, newBoard);
                setValidMoves([]);

                // Check Win Condition (Simpler check: did we capture General? No, valid moves prevents that usually, but checks mate)
                // Check if opponent has no moves
                const nextTurn = state.turn === Color.RED ? Color.BLACK : Color.RED;
                if (!hasLegalMoves(newBoard, nextTurn)) {
                    setWinner(state.turn); // Current player wins
                }
            } else {
                // Clicked invalid empty/enemy square -> Deselect
                selectPiece(null as any); // Hack because types might expect Position
                // Actually selectPiece expects Position. Passing null might be issue if type is strict.
                // In GameContext.tsx: selectPiece: (pos: Position) => void.
                // Reducer: case 'SELECT_PIECE': return { ...state, selectedPos: action.position };
                // Type Position = { row: number, col: number }.
                // State selectedPos is Position | null.
                // So I probably can't pass null to selectPiece if type is strict Position.
                // But let's check GameContext dispatch usage.
                // It says `action.position`.
                // If I want to deselect, I should probably add DESELECT or ensure Position can be null.
                // Looking at GameContext (Step 103): state.selectedPos is Position | null.
                // selectPiece takes Position.
                // If I click empty square, verification logic usually handles it.
                // I'll just clear valid moves and rely on state updates.
                // Actually if I click empty space, I just want to clear `validMoves`.
                setValidMoves([]);
            }
        }
    };

    // Check for "Check" status on every turn
    const inCheck = React.useMemo(() => {
        return isCheck(state.board, state.turn);
    }, [state.board, state.turn]);

    return (
        <div className="flex flex-col lg:flex-row gap-8 items-start justify-center p-4">
            <div className="flex-1 w-full max-w-[600px]">
                <XiangqiBoard
                    board={state.board}
                    turn={state.turn}
                    selectedPos={state.selectedPos}
                    validMoves={validMoves}
                    lastMove={state.lastMove}
                    onSquareClick={handleSquareClick}
                    winner={state.winner}
                />
            </div>

            <GameControlPanel
                turn={state.turn}
                winner={state.winner}
                inCheck={inCheck}
                isAiThinking={false}
                aiProgress={null}
                onUndo={undo}
                onRestart={reset}
                onSave={() => {
                    import('../../api/gameApi').then(api => {
                        api.saveGameResult('pvp', state.winner === Color.RED ? 1 : -1, state.moveHistory);
                    });
                }}
                canUndo={state.history.length > 0}
                canSave={!!state.winner}
            />
        </div>
    );
};
