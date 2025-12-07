/**
 * CategoryFilter - Filter games by Classical/RL category
 */
import React from 'react';
import { Bot, Users, ChevronDown } from 'lucide-react';

export type GameCategory = 'classical' | 'rl';

interface CategoryFilterProps {
    category: GameCategory;
    onCategoryChange: (category: GameCategory) => void;
    iterations?: number[];
    selectedIteration: number | null;
    onIterationChange: (iteration: number | null) => void;
}

export const CategoryFilter: React.FC<CategoryFilterProps> = ({
    category,
    onCategoryChange,
    iterations = [],
    selectedIteration,
    onIterationChange
}) => {
    return (
        <div className="px-4 py-3 border-b border-stone-100 space-y-3">
            {/* Category Tabs */}
            <div className="flex rounded-lg bg-stone-100 p-1">
                <button
                    onClick={() => onCategoryChange('classical')}
                    className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-md text-sm font-medium transition-all ${category === 'classical'
                            ? 'bg-white text-[#8b4513] shadow-sm'
                            : 'text-stone-500 hover:text-stone-700'
                        }`}
                >
                    <Users className="w-4 h-4" />
                    Classical
                </button>
                <button
                    onClick={() => onCategoryChange('rl')}
                    className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-md text-sm font-medium transition-all ${category === 'rl'
                            ? 'bg-white text-[#8b4513] shadow-sm'
                            : 'text-stone-500 hover:text-stone-700'
                        }`}
                >
                    <Bot className="w-4 h-4" />
                    RL Training
                </button>
            </div>

            {/* Iteration Filter (only for RL) */}
            {category === 'rl' && iterations.length > 0 && (
                <div className="relative">
                    <select
                        value={selectedIteration ?? ''}
                        onChange={(e) => onIterationChange(e.target.value ? Number(e.target.value) : null)}
                        className="w-full appearance-none bg-stone-50 border border-stone-200 rounded-lg py-2 px-3 pr-8 text-sm text-stone-700 focus:outline-none focus:ring-2 focus:ring-[#8b4513]/20 focus:border-[#8b4513]"
                    >
                        <option value="">All Iterations</option>
                        {iterations.map((iter) => (
                            <option key={iter} value={iter}>
                                Iteration {iter}
                            </option>
                        ))}
                    </select>
                    <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400 pointer-events-none" />
                </div>
            )}
        </div>
    );
};
