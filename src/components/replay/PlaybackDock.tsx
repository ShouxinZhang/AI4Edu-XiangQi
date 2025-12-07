import React, { useEffect, useState } from 'react';
import { Play, Pause, SkipBack, SkipForward, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '../common/Button';

interface PlaybackDockProps {
    currentStep: number;
    totalSteps: number;
    isPlaying: boolean;
    onPlayPause: () => void;
    onNext: () => void;
    onPrev: () => void;
    onGoToStart: () => void;
    onGoToEnd: () => void;
    onSeek: (step: number) => void;
}

export const PlaybackDock: React.FC<PlaybackDockProps> = ({
    currentStep,
    totalSteps,
    isPlaying,
    onPlayPause,
    onNext,
    onPrev,
    onGoToStart,
    onGoToEnd,
    onSeek
}) => {
    return (
        <div className="bg-white/90 backdrop-blur-md rounded-2xl shadow-xl border border-stone-200 p-2 flex flex-col gap-2">
            {/* Progress Bar */}
            <div className="px-2 pt-2">
                <input
                    type="range"
                    min={0}
                    max={totalSteps}
                    value={currentStep}
                    onChange={(e) => onSeek(parseInt(e.target.value))}
                    className="w-full h-1.5 bg-stone-200 rounded-lg appearance-none cursor-pointer accent-[#8b4513]"
                />
                <div className="flex justify-between text-[10px] text-stone-400 mt-1 font-mono">
                    <span>{currentStep}</span>
                    <span>{totalSteps}</span>
                </div>
            </div>

            {/* Controls */}
            <div className="flex items-center justify-between gap-1">
                <div className="flex items-center gap-1">
                    <Button variant="ghost" size="sm" onClick={onGoToStart} title="Start">
                        <SkipBack className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={onPrev} disabled={currentStep === 0} title="Prev">
                        <ChevronLeft className="w-4 h-4" />
                    </Button>
                </div>

                <Button
                    variant="primary"
                    className="rounded-full w-12 h-12 !p-0 shadow-lg hover:shadow-xl hover:scale-105 transition-all bg-[#8b4513]"
                    onClick={onPlayPause}
                >
                    {isPlaying ? <Pause className="w-5 h-5 fill-current" /> : <Play className="w-5 h-5 fill-current ml-0.5" />}
                </Button>

                <div className="flex items-center gap-1">
                    <Button variant="ghost" size="sm" onClick={onNext} disabled={currentStep >= totalSteps} title="Next">
                        <ChevronRight className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={onGoToEnd} title="End">
                        <SkipForward className="w-4 h-4" />
                    </Button>
                </div>
            </div>
        </div>
    );
};
