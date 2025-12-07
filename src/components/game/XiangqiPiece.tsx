import React from 'react';
import { Color, Piece } from '../../types';
import { PIECE_LABELS } from '../../constants';

interface PieceProps {
  piece: Piece;
  isSelected: boolean;
  onClick: () => void;
  className?: string;
}

const XiangqiPiece: React.FC<PieceProps> = ({ piece, isSelected, onClick, className = '' }) => {
  const isRed = piece.color === Color.RED;

  // Visual Styles
  const bgClass = 'bg-[#f0d9b5]'; // Wood/Ivory color
  const borderClass = isRed ? 'border-red-600' : 'border-neutral-900';
  const textClass = isRed ? 'text-red-600' : 'text-neutral-900';
  const ringClass = isSelected ? 'ring-4 ring-blue-500 z-10 scale-110' : 'shadow-md hover:scale-105';

  const label = PIECE_LABELS[`${piece.color}-${piece.type}`];

  return (
    <div
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
      className={`
        absolute w-[90%] h-[90%] left-[5%] top-[5%]
        rounded-full border-4 ${borderClass} ${bgClass}
        flex items-center justify-center
        cursor-pointer transition-all duration-200
        ${ringClass}
        ${className}
      `}
      style={{
        boxShadow: isSelected ? '0 0 15px rgba(59, 130, 246, 0.5)' : '2px 2px 4px rgba(0,0,0,0.4), inset 0 0 10px rgba(0,0,0,0.1)'
      }}
    >
      {/* Inner groove for 3D effect */}
      <div className={`w-[80%] h-[80%] rounded-full border ${isRed ? 'border-red-200' : 'border-neutral-400'} flex items-center justify-center`}>
        <span className={`text-2xl md:text-3xl font-bold font-serif select-none ${textClass}`} style={{ textShadow: '0px 1px 0px rgba(255,255,255,0.8)' }}>
          {label}
        </span>
      </div>
    </div>
  );
};

export default XiangqiPiece;
