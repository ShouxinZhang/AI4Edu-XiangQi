import React from 'react';
import { Color } from '../../types';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { RotateCcw, Undo2, BrainCircuit, Save, Settings2 } from 'lucide-react';
import { useGame } from '../../store/GameContext';

interface GameControlPanelProps {
    turn: Color;
    winner: Color | null;
    inCheck: boolean;
    isAiThinking: boolean;
    aiProgress: { percent: number, eta: number } | null;
    onUndo: () => void;
    onRestart: () => void;
    onSave: () => void;
    canUndo: boolean;
    canSave: boolean;
}

export const GameControlPanel: React.FC<GameControlPanelProps> = ({
    turn,
    winner,
    inCheck,
    isAiThinking,
    aiProgress,
    onUndo,
    onRestart,
    onSave,
    canUndo,
    canSave,
}) => {
    const { state, setDifficulty } = useGame();
    // Default to Level 2 if undefined
    const difficulty = state.difficulty || 2;

    return (
        <div className="w-full lg:w-80 space-y-4">
            {/* Game Status Card */}
            <Card title="Current Status" className="border-t-4 border-t-[#8b4513]">
                <div className="flex flex-col gap-4">

                    {/* Winner Banner */}
                    {winner ? (
                        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-xl text-center animate-bounce">
                            <div className="text-3xl mb-1">🏆</div>
                            <div className="font-bold text-lg text-yellow-800">
                                {winner === Color.RED ? 'Red Wins!' : 'Black Wins!'}
                            </div>
                        </div>
                    ) : (
                        <>
                            {/* Turn Indicator */}
                            <div className="flex items-center justify-between p-3 bg-stone-50 rounded-lg border border-stone-100">
                                <span className="text-stone-500 text-sm uppercase font-bold tracking-wider">To Move</span>
                                <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-bold ${turn === Color.RED ? 'bg-red-100 text-red-700' : 'bg-gray-800 text-white'
                                    }`}>
                                    <span className="w-2 h-2 rounded-full bg-current animate-pulse" />
                                    {turn === Color.RED ? 'RED (帥)' : 'BLACK (將)'}
                                </div>
                            </div>

                            {/* AI Status */}
                            {isAiThinking && (
                                <div className="flex flex-col gap-2 p-3 bg-blue-50/50 rounded-lg border border-blue-100/50">
                                    <div className="flex items-center justify-center gap-2 text-xs text-stone-500">
                                        <BrainCircuit className="w-3 h-3 animate-pulse text-blue-500" />
                                        <span>AI is calculating...</span>
                                    </div>

                                    {/* Progress Bar */}
                                    {aiProgress && (
                                        <div className="w-full space-y-1">
                                            <div className="flex justify-between text-[10px] text-stone-400">
                                                <span>{Math.round(aiProgress.percent)}%</span>
                                                <span>ETA: {aiProgress.eta.toFixed(1)}s</span>
                                            </div>
                                            <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
                                                <div
                                                    className="h-full bg-blue-500 transition-all duration-300 ease-out"
                                                    style={{ width: `${Math.round(aiProgress.percent)}%` }}
                                                />
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </>
                    )}

                    {/* Check Alert */}
                    {inCheck && !winner && (
                        <div className="px-4 py-2 bg-red-50 text-red-600 rounded-lg text-center font-bold text-sm border border-red-100 animate-pulse">
                            ⚠️ CHECK / 将军 !
                        </div>
                    )}
                </div>
            </Card>

            {/* Actions Card */}
            <Card title="Controls">
                <div className="space-y-3">
                    {/* Search Depth Selector */}
                    <div className="bg-stone-50 p-3 rounded-lg border border-stone-200 mb-2">
                        <label className="block text-xs font-bold text-stone-500 uppercase mb-1">
                            Search Depth (Ply)
                            <span className="ml-2 text-[10px] font-normal text-stone-400">Higher = Slower</span>
                        </label>
                        <div className="flex items-center gap-2">
                            <input
                                type="number"
                                min={1}
                                max={8}
                                value={difficulty}
                                onChange={(e) => setDifficulty(Math.max(1, Math.min(8, Number(e.target.value))))}
                                className="w-full p-2 text-sm bg-white border border-stone-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-center"
                                disabled={isAiThinking}
                            />
                            <div className="text-xs text-stone-400 w-12 text-right">
                                {difficulty <= 2 ? 'Fast' : difficulty <= 4 ? 'Medium' : 'Slow'}
                            </div>
                        </div>
                    </div>

                    <Button
                        variant="secondary"
                        className="w-full"
                        onClick={onRestart}
                        icon={<RotateCcw className="w-4 h-4" />}
                    >
                        Restart Game
                    </Button>

                    <Button
                        variant="outline"
                        className="w-full"
                        onClick={onUndo}
                        disabled={!canUndo || !!winner || isAiThinking}
                        icon={<Undo2 className="w-4 h-4" />}
                    >
                        Undo Move
                    </Button>

                    <Button
                        variant="primary"
                        className="w-full"
                        onClick={onSave}
                        disabled={!canSave}
                        icon={<Save className="w-4 h-4" />}
                    >
                        Save Game
                    </Button>
                </div>
            </Card>

            {/* Move History Logic Placeholder */}
            <Card title="Move History" className="opacity-50 pointer-events-none grayscale">
                <div className="h-32 flex items-center justify-center text-xs text-stone-400 italic">
                    Coming Soon...
                </div>
            </Card>

        </div>
    );
};
