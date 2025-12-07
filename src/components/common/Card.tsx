import React from 'react';

interface CardProps {
    children: React.ReactNode;
    className?: string;
    title?: string;
    subtitle?: string;
    actions?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
    children,
    className = '',
    title,
    subtitle,
    actions
}) => {
    return (
        <div className={`bg-white rounded-xl shadow-lg border border-stone-100 overflow-hidden ${className}`}>
            {(title || subtitle || actions) && (
                <div className="px-6 py-4 border-b border-stone-100 flex items-center justify-between bg-[#fdfbf7]/50">
                    <div>
                        {title && <h3 className="font-bold text-stone-800 text-lg">{title}</h3>}
                        {subtitle && <p className="text-sm text-stone-500 mt-0.5">{subtitle}</p>}
                    </div>
                    {actions && <div className="flex gap-2">{actions}</div>}
                </div>
            )}
            <div className="p-6">
                {children}
            </div>
        </div>
    );
};
