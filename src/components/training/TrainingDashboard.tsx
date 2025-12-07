import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { EvaluationPoint } from '../../types';

interface GpuStats {
    gpu_utilization: number;
    memory_used_mb: number;
    memory_total_mb: number;
    temperature_c: number;
    error?: string;
}

interface CpuStats {
    cpu_utilization: number;
    memory_used_mb: number;
    memory_total_mb: number;
    memory_percent: number;
    error?: string;
}

interface TrainingState {
    iteration: number;
    episode: number;
    total_episodes: number;
    step: number;
    status: string;
    history?: any[];
    evalHistory?: EvaluationPoint[]; // Added for evaluation metrics
}

const TrainingDashboard: React.FC = () => {
    const [gpuStats, setGpuStats] = useState<GpuStats | null>(null);
    const [cpuStats, setCpuStats] = useState<CpuStats | null>(null);
    const [trainingState, setTrainingState] = useState<TrainingState | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [gpuRes, cpuRes, trainRes] = await Promise.all([
                    fetch('http://localhost:8000/api/gpu/stats'),
                    fetch('http://localhost:8000/api/cpu/stats'),
                    fetch('http://localhost:8000/api/training/state')
                ]);
                setGpuStats(await gpuRes.json());
                setCpuStats(await cpuRes.json());
                setTrainingState(await trainRes.json());
            } catch (e) {
                console.error("Failed to fetch stats", e);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 2000); // Refresh every 2 seconds
        return () => clearInterval(interval);
    }, []);

    const vramPercent = gpuStats
        ? ((gpuStats.memory_used_mb / gpuStats.memory_total_mb) * 100).toFixed(1)
        : 0;

    return (
        <div className="bg-gradient-to-br from-gray-800 to-gray-900 p-6 rounded-xl shadow-lg text-white max-w-md">
            <h3 className="text-lg font-bold mb-4 text-amber-400">🖥️ Training Dashboard</h3>

            {/* CPU Stats */}
            <div className="mb-4">
                <div className="text-sm text-gray-400 mb-1">CPU Utilization</div>
                <div className="w-full bg-gray-700 rounded-full h-4 overflow-hidden">
                    <div
                        className="bg-purple-500 h-full transition-all duration-500"
                        style={{ width: `${cpuStats?.cpu_utilization || 0}%` }}
                    />
                </div>
                <div className="text-right text-xs text-gray-400 mt-1">{cpuStats?.cpu_utilization?.toFixed(1) || 0}%</div>
            </div>

            <div className="mb-4">
                <div className="text-sm text-gray-400 mb-1">RAM ({cpuStats?.memory_used_mb || 0} / {cpuStats?.memory_total_mb || 0} MB)</div>
                <div className="w-full bg-gray-700 rounded-full h-4 overflow-hidden">
                    <div
                        className="bg-pink-500 h-full transition-all duration-500"
                        style={{ width: `${cpuStats?.memory_percent || 0}%` }}
                    />
                </div>
                <div className="text-right text-xs text-gray-400 mt-1">{cpuStats?.memory_percent?.toFixed(1) || 0}%</div>
            </div>

            <hr className="border-gray-700 my-4" />

            {/* GPU Stats */}
            <div className="mb-4">
                <div className="text-sm text-gray-400 mb-1">GPU Utilization</div>
                <div className="w-full bg-gray-700 rounded-full h-4 overflow-hidden">
                    <div
                        className="bg-green-500 h-full transition-all duration-500"
                        style={{ width: `${gpuStats?.gpu_utilization || 0}%` }}
                    />
                </div>
                <div className="text-right text-xs text-gray-400 mt-1">{gpuStats?.gpu_utilization || 0}%</div>
            </div>

            <div className="mb-4">
                <div className="text-sm text-gray-400 mb-1">VRAM ({gpuStats?.memory_used_mb || 0} / {gpuStats?.memory_total_mb || 0} MB)</div>
                <div className="w-full bg-gray-700 rounded-full h-4 overflow-hidden">
                    <div
                        className="bg-blue-500 h-full transition-all duration-500"
                        style={{ width: `${vramPercent}%` }}
                    />
                </div>
                <div className="text-right text-xs text-gray-400 mt-1">{vramPercent}%</div>
            </div>

            <div className="mb-4 flex justify-between">
                <span className="text-gray-400">🌡️ Temperature</span>
                <span className={`font-mono ${(gpuStats?.temperature_c || 0) > 80 ? 'text-red-400' : 'text-green-400'}`}>
                    {gpuStats?.temperature_c || 0}°C
                </span>
            </div>

            <hr className="border-gray-700 my-4" />

            {/* Evaluation Metrics Chart */}
            {trainingState?.evalHistory && trainingState.evalHistory.length > 0 && (
                <div className="mb-4">
                    <h4 className="text-sm font-bold text-gray-300 mb-2">📈 Evaluation vs Classic AI</h4>
                    <div className="bg-gray-700/30 rounded p-2" style={{ height: 200 }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={trainingState.evalHistory}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                <XAxis dataKey="iteration" stroke="#888" fontSize={10} />
                                <YAxis domain={[0, 100]} stroke="#888" fontSize={10} tickFormatter={(v) => `${v}%`} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#333', border: 'none' }}
                                    labelStyle={{ color: '#fff' }}
                                />
                                <Legend wrapperStyle={{ fontSize: 10 }} />
                                <Line type="monotone" dataKey="vsLevel1" stroke="#4ade80" name="vs L1" dot={false} />
                                <Line type="monotone" dataKey="vsLevel2" stroke="#60a5fa" name="vs L2" dot={false} />
                                <Line type="monotone" dataKey="vsLevel3" stroke="#f97316" name="vs L3" dot={false} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}

            <hr className="border-gray-700 my-4" />

            {/* Training Progress */}
            <div className="text-sm text-gray-400 mb-1">Training Status: <span className="text-amber-300">{trainingState?.status || 'idle'}</span></div>

            <div className="grid grid-cols-2 gap-2 text-sm mt-2 mb-4">
                <div className="bg-gray-700/50 p-2 rounded">
                    <div className="text-gray-500">Iteration</div>
                    <div className="text-xl font-bold">{trainingState?.iteration || 0}</div>
                </div>
                <div className="bg-gray-700/50 p-2 rounded">
                    <div className="text-gray-500">Episode</div>
                    <div className="text-xl font-bold">{trainingState?.episode || 0} / {trainingState?.total_episodes || 10}</div>
                </div>
            </div>

            {/* Game History */}
            <h4 className="text-sm font-bold text-gray-300 mb-2">Recent Games</h4>
            <div className="bg-gray-700/30 rounded overflow-hidden max-h-48 overflow-y-auto text-xs">
                <table className="w-full text-left">
                    <thead className="bg-gray-700 text-gray-400">
                        <tr>
                            <th className="p-2">Winner</th>
                            <th className="p-2">Steps</th>
                            <th className="p-2">Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {(trainingState?.history || []).map((game: any, i: number) => (
                            <tr key={i} className="border-b border-gray-700/50 last:border-0 hover:bg-gray-700/50">
                                <td className="p-2">
                                    {game.winner === 1 ? <span className="text-red-400 font-bold">Red</span> :
                                        game.winner === -1 ? <span className="text-white font-bold">Black</span> :
                                            <span className="text-gray-400">Draw</span>}
                                </td>
                                <td className="p-2">{game.steps}</td>
                                <td className="p-2 text-gray-500">
                                    {new Date(game.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </td>
                            </tr>
                        ))}
                        {(!trainingState?.history || trainingState.history.length === 0) && (
                            <tr><td colSpan={3} className="p-4 text-center text-gray-500">No games finished yet</td></tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default TrainingDashboard;
