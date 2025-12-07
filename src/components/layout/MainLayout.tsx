import React from 'react';
import { Navbar } from './Navbar';
import { GameMode } from '../../types';

interface MainLayoutProps {
    children: React.ReactNode;
    currentMode: GameMode;
    onModeChange: (mode: GameMode) => void;
}

export const MainLayout: React.FC<MainLayoutProps> = ({
    children,
    currentMode,
    onModeChange,
}) => {
    return (
        <div className="min-h-screen bg-[#fdfbf7] text-stone-900 font-sans selection:bg-[#8b4513] selection:text-white">
            <Navbar currentMode={currentMode} onModeChange={onModeChange} />

            <main className="pt-24 pb-12 px-4 max-w-7xl mx-auto min-h-screen flex flex-col">
                {children}
            </main>

            <footer className="py-6 text-center text-stone-400 text-xs mt-auto">
                <p>© 2024 AI4Edu Xiangqi Project</p>
            </footer>
        </div>
    );
};
