
import React, { useEffect, useState } from 'react';
import XiangqiBoard from '../game/XiangqiBoard';
import TrainingDashboard from './TrainingDashboard';
import TrainingControlPanel from './TrainingControlPanel';
import { BoardState, Color, PieceType } from '../../types';
import { INITIAL_BOARD } from '../../constants';

const TrainingPage: React.FC = () => {
    const [board, setBoard] = useState<BoardState>(INITIAL_BOARD);
    const [status, setStatus] = useState<string>("Disconnected");
    const [step, setStep] = useState<number>(0);

    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8000/ws/training');

        ws.onopen = () => {
            setStatus("Connected to Training Server");
        };

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === 'step') {
                    const rawBoard = msg.data.board; // 10x9 array
                    setStep(msg.data.step);

                    // Convert raw board (int[][]) to BoardState
                    const newBoard: BoardState = rawBoard.map((row: number[]) =>
                        row.map((val: number) => {
                            if (val === 0) return null;
                            const color = val > 0 ? Color.RED : Color.BLACK;
                            const typeId = Math.abs(val);
                            let type = PieceType.SOLDIER;

                            switch (typeId) {
                                case 1: type = PieceType.GENERAL; break;
                                case 2: type = PieceType.ADVISOR; break;
                                case 3: type = PieceType.ELEPHANT; break;
                                case 4: type = PieceType.HORSE; break;
                                case 5: type = PieceType.CHARIOT; break;
                                case 6: type = PieceType.CANNON; break;
                                case 7: type = PieceType.SOLDIER; break;
                            }
                            return { type, color };
                        })
                    );
                    setBoard(newBoard);
                    setStatus(`Training... Step ${msg.data.step}`);
                }
            } catch (e) {
                console.error("Error parsing WebSocket message", e);
            }
        };

        ws.onclose = () => {
            setStatus("Disconnected (Training might handle stopped)");
        };

        return () => {
            ws.close();
        };
    }, []);

    return (
        <div className="flex flex-col items-center justify-center p-8">
            <h2 className="text-2xl font-bold mb-4 text-white">AlphaZero Training Monitor</h2>
            <div className="mb-4 text-gray-300">Status: {status}</div>

            <div className="flex gap-8 items-start">
                {/* Left: Dashboard */}
                <TrainingDashboard />

                {/* Right: Live Board */}
                <div className="bg-white/5 p-8 rounded-lg backdrop-blur-sm shadow-2xl w-[600px] shrink-0">
                    <XiangqiBoard
                        board={board}
                        turn={Color.RED}
                        selectedPos={null}
                        validMoves={[]}
                        onSquareClick={() => { }}
                        lastMove={null}
                        winner={null}
                    />
                </div>
            </div>

            {/* Training Control Panel */}
            <div className="mt-8 w-full max-w-2xl">
                <TrainingControlPanel isConnected={status.includes("Connected")} />
            </div>

            <div className="mt-4 text-gray-400 text-sm max-w-2xl text-center">
                Use the control panel above to start/stop training with custom parameters.
            </div>
        </div>
    );
};

export default TrainingPage;

