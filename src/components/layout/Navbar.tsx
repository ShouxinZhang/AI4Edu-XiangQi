import React from 'react';
import { GameMode } from '../../types';
import { User, Bot, BookOpen, History } from 'lucide-react';

interface NavbarProps {
    currentMode: GameMode;
    onModeChange: (mode: GameMode) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentMode, onModeChange }) => {
    const modes = [
        { id: GameMode.PVP, label: 'PvP', icon: <User className="w-4 h-4" /> },
        { id: GameMode.PVE, label: 'PvE (AI)', icon: <Bot className="w-4 h-4" /> },
        { id: GameMode.TRAINING, label: 'Training', icon: <BookOpen className="w-4 h-4" /> },
        { id: GameMode.REPLAY, label: 'Replay', icon: <History className="w-4 h-4" /> },
    ];

    return (
        <header className="fixed top-0 left-0 right-0 h-16 bg-white/90 backdrop-blur-md border-b border-stone-200 z-50 px-6 flex items-center justify-between shadow-sm">
            <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-[#8b4513] rounded-lg flex items-center justify-center text-white font-serif font-bold text-lg">
                    象
                </div>
                <h1 className="text-xl font-bold text-stone-800 tracking-wide font-serif">中國象棋 <span className="text-xs text-stone-500 font-sans font-normal ml-1">AI4Edu</span></h1>
            </div>

            <nav className="flex bg-stone-100 p-1 rounded-xl">
                {modes.map((mode) => (
                    <button
                        key={mode.id}
                        onClick={() => onModeChange(mode.id)}
                        className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${currentMode === mode.id
                                ? 'bg-[#8b4513] text-white shadow-sm'
                                : 'text-stone-600 hover:text-stone-900 hover:bg-stone-200/50'
                            }`}
                    >
                        {mode.icon}
                        {mode.label}
                    </button>
                ))}
            </nav>

            <div className="w-24 text-right text-xs text-stone-400">
                v0.1.0-beta
            </div>
        </header>
    );
};
