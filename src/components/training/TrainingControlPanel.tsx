/**
 * TrainingControlPanel - Control panel for starting/stopping training
 */
import React, { useEffect, useState } from 'react';
import { Play, Pause, Settings, Cpu, Layers, Save, RotateCcw } from 'lucide-react';
import { startTraining, stopTraining, resetTraining, getTrainingConfig, saveTrainingConfig, TrainingConfig } from '../../api/trainingApi';

interface TrainingControlPanelProps {
    isConnected?: boolean;
    selectedWorkerId?: number;
    onWorkerIdChange?: (id: number) => void;
}

const TrainingControlPanel: React.FC<TrainingControlPanelProps> = ({
    isConnected = false,
    selectedWorkerId = 0,
    onWorkerIdChange
}) => {
    const [isRunning, setIsRunning] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [isConfirmingReset, setIsConfirmingReset] = useState(false);
    const [config, setConfig] = useState<TrainingConfig>({
        max_steps: 200,
        workers: 4,
        mode: 'parallel',
        num_mcts_sims: 25,
        num_episodes: 10
    });

    // Load current config on mount
    useEffect(() => {
        loadConfig();
    }, []);

    const loadConfig = async () => {
        try {
            const response = await getTrainingConfig();
            setConfig(response.config);
            setIsRunning(response.is_running);
        } catch (e) {
            console.error('Failed to load training config:', e);
        }
    };

    const handleStart = async () => {
        setIsLoading(true);
        try {
            const response = await startTraining(config);
            if (response.status === 'ok') {
                setIsRunning(true);
            } else {
                alert(response.message || 'Failed to start training');
            }
        } catch (e) {
            console.error('Failed to start training:', e);
            alert('Failed to start training');
        }
        setIsLoading(false);
    };

    const handleStop = async () => {
        setIsLoading(true);
        try {
            const response = await stopTraining();
            if (response.status === 'ok') {
                setIsRunning(false);
            }
        } catch (e) {
            console.error('Failed to stop training:', e);
        }
        setIsLoading(false);
    };

    // Two-click reset: First click shows "Confirm?", second click executes
    const handleResetClick = async (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();

        if (!isConfirmingReset) {
            // First click: Enter confirmation mode
            setIsConfirmingReset(true);
            // Auto-cancel after 5 seconds
            setTimeout(() => setIsConfirmingReset(false), 5000);
            return;
        }

        // Second click: Execute reset
        setIsConfirmingReset(false);
        setIsLoading(true);
        try {
            const response = await resetTraining();
            if (response.status === 'ok') {
                setIsRunning(false);
                // Success - data cleared
            } else {
                alert(response.message || "Failed to reset");
            }
        } catch (err: any) {
            console.error('Failed to reset:', err);
            alert('Failed to reset training: ' + (err.message || String(err)));
        }
        setIsLoading(false);
    };

    const handleSave = async () => {
        setIsSaving(true);
        try {
            const response = await saveTrainingConfig(config);
            if (response.status === 'ok') {
                alert('Configuration saved!');
            }
        } catch (e) {
            console.error('Failed to save config:', e);
            alert('Failed to save configuration');
        }
        setIsSaving(false);
    };

    return (
        <div className="bg-gradient-to-r from-stone-800 to-stone-900 rounded-xl p-6 shadow-lg border border-stone-700">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Settings className="w-5 h-5 text-amber-400" />
                    <h3 className="text-lg font-bold text-white">Training Control</h3>
                </div>
                <button
                    type="button"
                    onClick={handleSave}
                    disabled={isSaving || isRunning}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-stone-700 hover:bg-stone-600 text-stone-300 hover:text-white rounded-lg text-sm transition-all disabled:opacity-50"
                >
                    <Save className="w-4 h-4" />
                    {isSaving ? 'Saving...' : 'Save Config'}
                </button>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
                {/* Max Steps */}
                <div>
                    <label className="block text-xs text-stone-400 mb-1">Max Steps</label>
                    <input
                        type="number"
                        value={config.max_steps}
                        onChange={(e) => setConfig({ ...config, max_steps: parseInt(e.target.value) || 200 })}
                        disabled={isRunning}
                        className="w-full bg-stone-700 border border-stone-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 disabled:opacity-50"
                    />
                </div>

                {/* Episodes Input */}
                <div className="flex flex-col gap-2">
                    <label className="text-stone-400 text-xs flex items-center gap-1">
                        <Settings className="w-3 h-3" /> Episodes/Iter
                        <span className="text-stone-600 cursor-help" title="Number of self-play games to play per iteration (per worker per batch)">ⓘ</span>
                    </label>
                    <input
                        type="number"
                        min="1"
                        max="1000"
                        value={config.num_episodes || 10}
                        onChange={(e) => setConfig({ ...config, num_episodes: parseInt(e.target.value) || 10 })}
                        disabled={isRunning}
                        className="bg-stone-800 border border-stone-700 rounded px-3 py-2 text-sm text-stone-200 focus:outline-none focus:border-amber-600 disabled:opacity-50"
                    />
                </div>

                {/* Workers Input (Changed from Select to Number) */}
                <div className="flex flex-col gap-2">
                    <label className="text-stone-400 text-xs flex items-center gap-1">
                        <Settings className="w-3 h-3" /> Workers
                    </label>
                    <input
                        type="number"
                        min="1"
                        max="64"
                        value={config.workers}
                        onChange={(e) => setConfig({ ...config, workers: parseInt(e.target.value) || 1 })}
                        disabled={isRunning}
                        className="bg-stone-800 border border-stone-700 rounded px-3 py-2 text-sm text-stone-200 focus:outline-none focus:border-amber-600 disabled:opacity-50"
                    />
                </div>

                {/* Watch Worker (Real-time View) */}
                <div className="flex flex-col gap-2">
                    <label className="text-stone-400 text-xs flex items-center gap-1">
                        👀 Watch Worker #
                        <span className="text-stone-600 cursor-help" title="Select which worker's game to show in real-time">ⓘ</span>
                    </label>
                    <input
                        type="number"
                        min="0"
                        max={config.workers - 1}
                        value={selectedWorkerId}
                        onChange={(e) => onWorkerIdChange?.(parseInt(e.target.value) || 0)}
                        className="bg-stone-800 border border-stone-700 rounded px-3 py-2 text-sm text-stone-200 focus:outline-none focus:border-amber-600"
                    />
                </div>
                <div>
                    <label className="block text-xs text-stone-400 mb-1 flex items-center gap-1">
                        <Layers className="w-3 h-3" /> Mode
                    </label>
                    <select
                        value={config.mode}
                        onChange={(e) => setConfig({ ...config, mode: e.target.value as 'single' | 'parallel' })}
                        disabled={isRunning}
                        className="w-full bg-stone-700 border border-stone-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 disabled:opacity-50"
                    >
                        <option value="single">Single (CPU+GPU)</option>
                        <option value="parallel">Parallel (Multi-worker)</option>
                    </select>
                </div>

                {/* MCTS Sims */}
                <div>
                    <label className="block text-xs text-stone-400 mb-1">MCTS Simulations</label>
                    <input
                        type="number"
                        value={config.num_mcts_sims}
                        onChange={(e) => setConfig({ ...config, num_mcts_sims: parseInt(e.target.value) || 25 })}
                        disabled={isRunning}
                        className="w-full bg-stone-700 border border-stone-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 disabled:opacity-50"
                    />
                </div>
            </div>

            {/* Control Buttons */}
            <div className="flex gap-3">
                {!isRunning ? (
                    <button
                        type="button"
                        onClick={handleStart}
                        disabled={isLoading}
                        className="flex-grow flex items-center justify-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-bold py-3 px-6 rounded-lg transition-all disabled:opacity-50"
                    >
                        <Play className="w-5 h-5" />
                        {isLoading ? 'Starting...' : 'Start Training'}
                    </button>
                ) : (
                    <button
                        type="button"
                        onClick={handleStop}
                        disabled={isLoading}
                        className="flex-grow flex items-center justify-center gap-2 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold py-3 px-6 rounded-lg transition-all disabled:opacity-50"
                    >
                        <Pause className="w-5 h-5" />
                        {isLoading ? 'Stopping...' : 'Stop Training'}
                    </button>
                )}

                {/* Restart/Reset Button - Two-click confirmation */}
                <button
                    type="button"
                    onClick={handleResetClick}
                    disabled={isLoading}
                    className={`flex items-center justify-center gap-2 font-bold py-3 px-4 rounded-lg transition-all disabled:opacity-50 border ${isConfirmingReset
                        ? 'bg-red-600 hover:bg-red-500 text-white border-red-500 animate-pulse'
                        : 'bg-stone-700 hover:bg-stone-600 text-amber-500 hover:text-amber-400 border-stone-600'
                        }`}
                    title={isConfirmingReset ? "Click again to confirm reset!" : "Reset/Clear Data"}
                >
                    <RotateCcw className="w-5 h-5" />
                    <span className="text-xs">{isConfirmingReset ? '确认删除?' : 'RESET'}</span>
                </button>
            </div>

            {isRunning && (
                <div className="mt-4 text-center text-sm text-green-400">
                    ● Training is running...
                </div>
            )}
        </div>
    );
};

export default TrainingControlPanel;

