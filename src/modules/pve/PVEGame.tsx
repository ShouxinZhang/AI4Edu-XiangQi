import React, { useEffect, useState, useRef } from 'react';
import XiangqiBoard from '../../components/game/XiangqiBoard';
import { GameControlPanel } from '../../components/layout/GameControlPanel';
import { useGame } from '../../store/GameContext';
import { getValidMoves, hasLegalMoves, isCheck } from '../../utils/gameLogic';
import { getAIMove, saveGameResult } from '../../api/gameApi';
import { Color, Position } from '../../types';

export const PVEGame: React.FC = () => {
    const { state, selectPiece, makeMove, setWinner, undo, reset } = useGame();
    const [validMoves, setValidMoves] = useState<Position[]>([]);
    const [isAiThinking, setIsAiThinking] = useState(false);
    const [aiProgress, setAiProgress] = useState<{ percent: number, eta: number } | null>(null);

    // Player is always Red for now (User plays bottom)
    const PLAYER_COLOR = Color.RED;

    // AbortController for AI requests
    const abortControllerRef = useRef<AbortController | null>(null);

    useEffect(() => {
        // AI Turn
        if (!state.winner && state.turn !== PLAYER_COLOR) {
            const makeAIMove = async () => {
                setIsAiThinking(true);
                setAiProgress(null);

                // Cancel previous request if any
                if (abortControllerRef.current) {
                    abortControllerRef.current.abort();
                }
                abortControllerRef.current = new AbortController();

                try {
                    const result = await getAIMove(
                        // Convert board to number[][] if needed by API? 
                        // Backend expects number[][]. 
                        // My board is (Piece | null)[][]. 
                        // I need a converter.
                        state.board.map(row => row.map(p => {
                            if (!p) return 0;
                            // classic/evaluation.py or game.py encoding?
                            // Backend game.py usually uses:
                            // Red: positive, Black: negative.
                            // General: 1, Advisor: 2, Elephant: 3, Horse: 4, Rook: 5, Cannon: 6, Pawn: 7
                            const typeMap: Record<string, number> = {
                                'general': 1, 'advisor': 2, 'elephant': 3, 'horse': 4, 'chariot': 5, 'cannon': 6, 'soldier': 7
                            };
                            const val = typeMap[p.type] || 0;
                            return p.color === Color.RED ? val : -val;
                        })),
                        -1, // AI is Black (-1)
                        state.difficulty,
                        abortControllerRef.current.signal,
                        (percent, eta) => setAiProgress({ percent, eta })
                    );

                    // Apply AI Move
                    const { start, end } = result;
                    // start/end are [row, col] or [x, y]?
                    // Backend MoveResponse: start: Tuple[int, int], end: Tuple[int, int]
                    // They are [row, col].

                    const fromPos = { row: start[0], col: start[1] };
                    const toPos = { row: end[0], col: end[1] };

                    const newBoard = state.board.map(row => [...row]);
                    newBoard[toPos.row][toPos.col] = newBoard[fromPos.row][fromPos.col];
                    newBoard[fromPos.row][fromPos.col] = null;

                    makeMove(fromPos, toPos, newBoard);

                    // Check Win
                    if (!hasLegalMoves(newBoard, PLAYER_COLOR)) {
                        setWinner(Color.BLACK);
                    }

                } catch (error: any) {
                    if (error.name !== 'AbortError') {
                        console.error("AI Error:", error);
                    }
                } finally {
                    setIsAiThinking(false);
                    setAiProgress(null);
                    abortControllerRef.current = null;
                }
            };

            makeAIMove();
        }

        // Cleanup on unmount or turn change (if interrupted)
        return () => {
            // Don't abort here immediately on every render, strictly control.
            // But if component unmounts, yes.
        };
    }, [state.turn, state.winner, state.difficulty]); // Dependency on turn triggers AI

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }
        };
    }, []);


    const handleSquareClick = (pos: Position) => {
        // Player interaction only during player turn
        if (state.turn !== PLAYER_COLOR || state.winner || isAiThinking) return;

        const piece = state.board[pos.row][pos.col];
        const isMyPiece = piece && piece.color === state.turn;

        if (isMyPiece) {
            selectPiece(pos);
            const moves = getValidMoves(state.board, pos);
            setValidMoves(moves);
        } else if (state.selectedPos) {
            const isMoveValid = validMoves.some(m => m.row === pos.row && m.col === pos.col);
            if (isMoveValid) {
                const from = state.selectedPos;
                const to = pos;
                const newBoard = state.board.map(row => [...row]);
                newBoard[to.row][to.col] = newBoard[from.row][from.col];
                newBoard[from.row][from.col] = null;

                makeMove(from, to, newBoard);
                setValidMoves([]);

                if (!hasLegalMoves(newBoard, Color.BLACK)) {
                    setWinner(Color.RED);
                }
            } else {
                setValidMoves([]);
            }
        }
    };

    const inCheck = React.useMemo(() => isCheck(state.board, state.turn), [state.board, state.turn]);

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
                isAiThinking={isAiThinking}
                aiProgress={aiProgress}
                onUndo={undo}
                onRestart={() => {
                    // Abort current calculation
                    if (abortControllerRef.current) abortControllerRef.current.abort();
                    reset();
                }}
                onSave={() => {
                    saveGameResult('pve', state.winner === Color.RED ? 1 : -1, state.moveHistory); // 1 = Red Win (Player), -1 = Black Win (AI)
                }}
                canUndo={state.history.length > 0 && !isAiThinking} // Prevent undo while AI thinking
                canSave={!!state.winner}
            />
        </div>
    );
};
