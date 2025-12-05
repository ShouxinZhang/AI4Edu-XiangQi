import React, { useMemo } from 'react';
import { BoardState, Color, Position } from '../types';
import XiangqiPiece from './XiangqiPiece';

interface BoardProps {
  board: BoardState;
  turn: Color;
  selectedPos: Position | null;
  validMoves: Position[];
  lastMove: { from: Position; to: Position } | null;
  onSquareClick: (pos: Position) => void;
  winner: Color | null;
}

const XiangqiBoard: React.FC<BoardProps> = ({
  board,
  selectedPos,
  validMoves,
  lastMove,
  onSquareClick,
  winner,
}) => {
  // SVG Grid Generation
  const GridLines = useMemo(() => {
    const lines = [];
    
    // Horizontal Lines (10 rows)
    for (let i = 0; i < 10; i++) {
      const y = i * 10 + 5;
      lines.push(<line key={`h-${i}`} x1="5" y1={y} x2="85" y2={y} stroke="#5c4033" strokeWidth="0.5" />);
    }

    // Vertical Lines (9 cols) - Split by River
    for (let i = 0; i < 9; i++) {
      const x = i * 10 + 5;
      // Top half (rows 0-4)
      lines.push(<line key={`v-top-${i}`} x1={x} y1="5" x2={x} y2="45" stroke="#5c4033" strokeWidth="0.5" />);
      // Bottom half (rows 5-9)
      lines.push(<line key={`v-bot-${i}`} x1={x} y1="55" x2={x} y2="95" stroke="#5c4033" strokeWidth="0.5" />);
      
      // Connect river sides for edge columns only
      if (i === 0 || i === 8) {
         lines.push(<line key={`v-river-${i}`} x1={x} y1="45" x2={x} y2="55" stroke="#5c4033" strokeWidth="0.5" />);
      }
    }

    // Palaces (Diagonals)
    // Top: (3,0) to (5,2) and (5,0) to (3,2) -> x: 35-55, y: 5-25
    lines.push(<line key="p-top-1" x1="35" y1="5" x2="55" y2="25" stroke="#5c4033" strokeWidth="0.5" />);
    lines.push(<line key="p-top-2" x1="55" y1="5" x2="35" y2="25" stroke="#5c4033" strokeWidth="0.5" />);
    
    // Bottom: (3,7) to (5,9) and (5,7) to (3,9) -> x: 35-55, y: 75-95
    lines.push(<line key="p-bot-1" x1="35" y1="75" x2="55" y2="95" stroke="#5c4033" strokeWidth="0.5" />);
    lines.push(<line key="p-bot-2" x1="55" y1="75" x2="35" y2="95" stroke="#5c4033" strokeWidth="0.5" />);

    // Markers (the little crosses for initial positions)
    // Helper to draw a corner marker
    const drawMarker = (r: number, c: number) => {
       const x = c * 10 + 5;
       const y = r * 10 + 5;
       const g = 1; // gap from intersection
       const l = 3; // length of marker line
       const els = [];
       // Top-Left
       if (c > 0) els.push(<path key={`m-${r}-${c}-tl`} d={`M ${x-g-l} ${y-g} L ${x-g} ${y-g} L ${x-g} ${y-g-l}`} fill="none" stroke="#5c4033" strokeWidth="0.5" />);
       // Top-Right
       if (c < 8) els.push(<path key={`m-${r}-${c}-tr`} d={`M ${x+g} ${y-g-l} L ${x+g} ${y-g} L ${x+g+l} ${y-g}`} fill="none" stroke="#5c4033" strokeWidth="0.5" />);
       // Bottom-Left
       if (c > 0) els.push(<path key={`m-${r}-${c}-bl`} d={`M ${x-g-l} ${y+g} L ${x-g} ${y+g} L ${x-g} ${y+g+l}`} fill="none" stroke="#5c4033" strokeWidth="0.5" />);
       // Bottom-Right
       if (c < 8) els.push(<path key={`m-${r}-${c}-br`} d={`M ${x+g+l} ${y+g} L ${x+g} ${y+g} L ${x+g} ${y+g+l}`} fill="none" stroke="#5c4033" strokeWidth="0.5" />);
       return els;
    };

    // Cannon markers
    lines.push(...drawMarker(2, 1));
    lines.push(...drawMarker(2, 7));
    lines.push(...drawMarker(7, 1));
    lines.push(...drawMarker(7, 7));

    // Soldier markers
    for (let c = 0; c <= 8; c += 2) {
      lines.push(...drawMarker(3, c));
      lines.push(...drawMarker(6, c));
    }

    return lines;
  }, []);

  return (
    <div className="relative select-none w-full max-w-[600px] aspect-[9/10] bg-[#eecfa1] shadow-2xl rounded-lg p-2 md:p-4 border-4 border-[#8b5a2b]">
      {/* SVG Grid Layer */}
      <svg viewBox="0 0 90 100" className="absolute inset-0 w-full h-full pointer-events-none z-0 p-2 md:p-4 box-border">
        {GridLines}
        {/* River Text */}
        <text x="25" y="52" fontSize="4" textAnchor="middle" fill="#5c4033" style={{ writingMode: 'horizontal-tb' }} className="font-serif">楚 河</text>
        <text x="65" y="52" fontSize="4" textAnchor="middle" fill="#5c4033" style={{ writingMode: 'horizontal-tb' }} className="font-serif">漢 界</text>
      </svg>

      {/* Interaction Layer - Grid of Squares */}
      <div className="relative w-full h-full grid grid-cols-9 grid-rows-10 z-10">
        {board.map((row, r) =>
          row.map((piece, c) => {
            const isSelected = selectedPos?.row === r && selectedPos?.col === c;
            const isValidMove = validMoves.some(m => m.row === r && m.col === c);
            const isLastMoveFrom = lastMove?.from.row === r && lastMove?.from.col === c;
            const isLastMoveTo = lastMove?.to.row === r && lastMove?.to.col === c;

            return (
              <div
                key={`${r}-${c}`}
                className="relative w-full h-full flex items-center justify-center"
                onClick={() => !winner && onSquareClick({ row: r, col: c })}
              >
                {/* Last Move Indicator (Highlight Square Background) */}
                {(isLastMoveFrom || isLastMoveTo) && (
                   <div className="absolute inset-1 bg-blue-600/30 rounded z-0" />
                )}
                
                {/* Marker for 'From' (Empty Source) */}
                {isLastMoveFrom && !piece && (
                   <div className="absolute w-2 h-2 bg-blue-800/50 rounded-full z-0" />
                )}

                {/* Valid Move Indicator (Dot or Ring) */}
                {isValidMove && !piece && (
                  <div className="absolute w-3 h-3 md:w-4 md:h-4 bg-green-600 rounded-full opacity-60 animate-pulse z-10" />
                )}
                {isValidMove && piece && (
                  <div className="absolute w-full h-full border-4 border-red-500 rounded-full animate-pulse z-20 pointer-events-none" />
                )}

                {/* Piece */}
                {piece && (
                  <XiangqiPiece
                    piece={piece}
                    isSelected={isSelected}
                    onClick={() => !winner && onSquareClick({ row: r, col: c })}
                  />
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default XiangqiBoard;
