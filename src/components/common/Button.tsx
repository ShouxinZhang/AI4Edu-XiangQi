import React from 'react';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg';
    isLoading?: boolean;
    icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
    children,
    variant = 'primary',
    size = 'md',
    isLoading = false,
    icon,
    className = '',
    disabled,
    ...props
}) => {
    const baseStyles = "inline-flex items-center justify-center rounded-xl font-medium transition-all focus:outline-none focus:ring-2 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed";

    const variants = {
        primary: "bg-[#8b4513] text-white hover:bg-[#703810] focus:ring-[#8b4513] shadow-md hover:shadow-lg active:scale-95",
        secondary: "bg-[#d4a017] text-white hover:bg-[#b88b14] focus:ring-[#d4a017] shadow-md",
        outline: "border-2 border-[#8b4513] text-[#8b4513] hover:bg-[#8b4513]/10",
        ghost: "bg-transparent text-stone-600 hover:bg-stone-100 hover:text-stone-900",
        danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-600 shadow-sm",
    };

    const sizes = {
        sm: "px-3 py-1.5 text-xs gap-1.5",
        md: "px-4 py-2 text-sm gap-2",
        lg: "px-6 py-3 text-base gap-2.5",
    };

    return (
        <button
            className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
            disabled={disabled || isLoading}
            {...props}
        >
            {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
            ) : icon ? (
                <span className="flex items-center">{icon}</span>
            ) : null}

            {children && <span>{children}</span>}
        </button>
    );
};
