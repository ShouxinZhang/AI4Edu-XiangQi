/**
 * ReplayPage - Game replay viewer with playback controls
 */
import React, { useEffect, useState } from 'react';
import { useReplay, ReplayProvider } from '../store/ReplayContext';
import { getGameHistory, getEvolutionGames, getEvolutionIterations } from '../api';
import { RefreshCw } from 'lucide-react';
import { ReplayLayout } from '../components/replay/ReplayLayout';
import { GameHistoryCard, GameHistoryItem } from '../components/replay/GameHistoryCard';
import { CategoryFilter, GameCategory } from '../components/replay/CategoryFilter';
import { PlaybackDock } from '../components/replay/PlaybackDock';
import XiangqiBoard from '../components/game/XiangqiBoard';
import { BoardState, Color } from '../types';

const ReplayPageContent: React.FC = () => {
    const { state, loadGameFromData, nextStep, prevStep, goToStep, reset: resetReplay } = useReplay();
    const [games, setGames] = useState<GameHistoryItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [isPlaying, setIsPlaying] = useState(false);
    const [selectedGameId, setSelectedGameId] = useState<string | null>(null);

    // Category filter state
    const [category, setCategory] = useState<GameCategory>('classical');
    const [iterations, setIterations] = useState<number[]>([]);
    const [selectedIteration, setSelectedIteration] = useState<number | null>(null);

    // Load Game History based on category
    useEffect(() => {
        loadGames();
    }, [category, selectedIteration]);


    const loadGames = async () => {
        setLoading(true);
        try {
            if (category === 'classical') {
                // Load Classical games (PvP, PvE)
                const [pvpData, pveData] = await Promise.all([
                    getGameHistory('pvp', 30),
                    getGameHistory('pve', 30),
                ]);
                const allGames = [...pvpData, ...pveData].map(g => ({ ...g, source: 'classical' })) as GameHistoryItem[];
                allGames.sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
                setGames(allGames.slice(0, 50));
            } else {
                // Load RL evolution games
                // First load iterations if not loaded
                if (iterations.length === 0) {
                    const iters = await getEvolutionIterations();
                    setIterations(iters);
                }
                const rlGames = await getEvolutionGames(selectedIteration ?? undefined, 50);
                setGames(rlGames as GameHistoryItem[]);
            }
        } catch (e) {
            console.error('Failed to load games:', e);
        }
        setLoading(false);
    };

    // Auto-play effect
    useEffect(() => {
        if (!isPlaying) return;

        const timer = setInterval(() => {
            if (state.currentStep >= state.boards.length - 1) {
                setIsPlaying(false);
            } else {
                nextStep();
            }
        }, 1000);

        return () => clearInterval(timer);
    }, [isPlaying, state.currentStep, state.boards.length, nextStep]);

    const handleSelectGame = (game: GameHistoryItem) => {
        setSelectedGameId(game.game_id);
        // Load game directly from the moves data
        if (game.moves && Array.isArray(game.moves)) {
            loadGameFromData(game.game_id, game.moves);
        }
        setIsPlaying(false);
    };

    // Sidebar: Game List
    const SidebarContent = (
        <div className="h-full flex flex-col">
            <div className="px-6 py-4 border-b border-stone-100 bg-stone-50/50">
                <h2 className="font-bold text-stone-700">Recent Games</h2>
                <p className="text-xs text-stone-400">Select a game to replay</p>
            </div>

            {/* Category Filter */}
            <CategoryFilter
                category={category}
                onCategoryChange={(c) => {
                    setCategory(c);
                    setSelectedIteration(null);
                    setGames([]);
                }}
                iterations={iterations}
                selectedIteration={selectedIteration}
                onIterationChange={setSelectedIteration}
            />

            <div className="flex-grow overflow-y-auto">
                {loading ? (
                    <div className="flex justify-center p-8">
                        <RefreshCw className="w-6 h-6 animate-spin text-stone-300" />
                    </div>
                ) : games.length === 0 ? (
                    <div className="p-8 text-center text-stone-400 text-sm">
                        {category === 'rl' ? 'No RL training games found.' : 'No game history found.'}
                    </div>
                ) : (
                    games.map((game, i) => (
                        <GameHistoryCard
                            key={game.game_id || i}
                            game={game}
                            index={i}
                            isSelected={selectedGameId === game.game_id}
                            onClick={() => handleSelectGame(game)}
                        />
                    ))
                )}
            </div>
        </div>
    );

    // Board Content
    const BoardContent = (
        <div className="w-full max-w-[500px] mx-auto">
            {state.gameId && state.boards && state.boards.length > 0 ? (
                <XiangqiBoard
                    board={state.boards[state.currentStep]}
                    turn={state.currentStep % 2 === 0 ? Color.RED : Color.BLACK}
                    selectedPos={null}
                    validMoves={[]}
                    lastMove={state.moves?.[state.currentStep - 1] ? { from: state.moves[state.currentStep - 1].from, to: state.moves[state.currentStep - 1].to } : null}
                    onSquareClick={() => { }}
                    winner={null}
                />
            ) : (
                <div className="flex flex-col items-center justify-center p-12 text-stone-400 border-2 border-dashed border-stone-200 rounded-xl bg-stone-50/50">
                    <span className="font-serif italic text-xl mb-2">Select a game to start replay</span>
                    <span className="text-sm">Choose from the history list on the left</span>
                </div>
            )}
        </div>
    );

    // Dock Content
    const DockContent = state.boards.length > 1 ? (
        <PlaybackDock
            currentStep={state.currentStep}
            totalSteps={state.boards.length - 1}
            isPlaying={isPlaying}
            onPlayPause={() => setIsPlaying(!isPlaying)}
            onNext={nextStep}
            onPrev={prevStep}
            onGoToStart={() => goToStep(0)}
            onGoToEnd={() => goToStep(state.boards.length - 1)}
            onSeek={goToStep}
        />
    ) : null;

    return (
        <ReplayLayout
            sidebar={SidebarContent}
            board={BoardContent}
            dock={DockContent}
        />
    );
};

const ReplayPage: React.FC = () => {
    return (
        <ReplayProvider>
            <ReplayPageContent />
        </ReplayProvider>
    );
};

export default ReplayPage;
