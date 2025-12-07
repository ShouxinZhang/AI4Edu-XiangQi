import React from 'react';

interface ReplayLayoutProps {
    sidebar: React.ReactNode;
    board: React.ReactNode;
    dock: React.ReactNode;
}

export const ReplayLayout: React.FC<ReplayLayoutProps> = ({
    sidebar,
    board,
    dock
}) => {
    return (
        <div className="flex flex-col lg:flex-row h-[calc(100vh-8rem)] gap-6">
            {/* Left Sidebar - Game List */}
            <aside className="w-full lg:w-80 flex-shrink-0 bg-white rounded-xl shadow-lg border border-stone-100 overflow-hidden flex flex-col">
                {sidebar}
            </aside>

            {/* Main Stage - Board */}
            <section className="flex-grow relative flex flex-col items-center justify-center bg-stone-100/50 rounded-xl border border-stone-200/50">
                {board}

                {/* Playback Dock */}
                <div className="absolute bottom-6 left-1/2 -translate-x-1/2 w-full max-w-lg px-4">
                    {dock}
                </div>
            </section>
        </div>
    );
};
