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
                                <div className="flex items-center justify-center gap-2 text-xs text-stone-500 p-2 bg-blue-50/50 rounded-lg border border-blue-100/50">
                                    <BrainCircuit className="w-3 h-3 animate-pulse text-blue-500" />
                                    AI is calculating...
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
                    {/* Difficulty Selector */}
                    <div className="bg-stone-50 p-3 rounded-lg border border-stone-200 mb-2">
                        <label className="block text-xs font-bold text-stone-500 uppercase mb-1">AI Difficulty</label>
                        <select
                            value={difficulty}
                            onChange={(e) => setDifficulty(Number(e.target.value))}
                            className="w-full p-2 text-sm bg-white border border-stone-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            disabled={isAiThinking}
                        >
                            <option value={1}>Level 1 (Beginner)</option>
                            <option value={2}>Level 2 (Amateur)</option>
                            <option value={3}>Level 3 (Club)</option>
                            <option value={4}>Level 4 (Strong)</option>
                            <option value={5}>AlphaZero (Neural Net)</option>
                        </select>
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
