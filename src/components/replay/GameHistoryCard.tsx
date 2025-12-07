import React from 'react';
import { Trophy, Skull, Handshake, Clock, Bot, Users } from 'lucide-react';

export interface GameHistoryItem {
    game_id: string;
    timestamp: number;
    winner: number;
    moves: number[][]; // [from, to]...
    iteration?: number;  // RL training iteration
    source?: 'classical' | 'rl';
}

interface GameHistoryCardProps {
    game: GameHistoryItem;
    isSelected?: boolean;
    onClick: () => void;
    index: number;
}

export const GameHistoryCard: React.FC<GameHistoryCardProps> = ({
    game,
    isSelected,
    onClick,
    index
}) => {
    const date = new Date(game.timestamp * 1000);

    // Determine icon and color based on winner
    // 1 = Red Win, -1 = Black Win, 0 = Draw
    let OutcomeIcon = Handshake;
    let colorClass = "text-stone-500 bg-stone-100";
    let label = "Draw";

    if (game.winner === 1) {
        OutcomeIcon = Trophy;
        colorClass = "text-red-600 bg-red-100";
        label = "Red Won";
    } else if (game.winner === -1) {
        OutcomeIcon = Skull; // Or Trophy if viewing as Black
        colorClass = "text-stone-800 bg-stone-200";
        label = "Black Won";
    }

    const isRLGame = game.source === 'rl' || game.iteration !== undefined;

    return (
        <button
            onClick={onClick}
            className={`w-full text-left p-4 border-b border-stone-100 hover:bg-stone-50 transition-all group ${isSelected ? 'bg-amber-50 border-l-4 border-l-[#8b4513]' : 'border-l-4 border-l-transparent'
                }`}
        >
            <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-stone-400">#{index + 1}</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-bold flex items-center gap-1 ${colorClass}`}>
                        <OutcomeIcon className="w-3 h-3" /> {label}
                    </span>
                </div>
                <div className="text-[10px] text-stone-400 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
            </div>

            <div className="flex justify-between items-end">
                <div className="text-sm font-medium text-stone-700 group-hover:text-[#8b4513] transition-colors flex items-center gap-1.5">
                    {isRLGame ? (
                        <>
                            <Bot className="w-3.5 h-3.5 text-purple-500" />
                            <span>Iter {game.iteration}</span>
                        </>
                    ) : (
                        <>
                            <Users className="w-3.5 h-3.5 text-stone-400" />
                            <span>vs AI</span>
                        </>
                    )}
                </div>
                <div className="text-xs text-stone-500">
                    {game.moves?.length || 0} moves
                </div>
            </div>
        </button>
    );
};

