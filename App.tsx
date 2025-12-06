import React, { useState, useEffect, useCallback, useRef } from 'react';
import { BoardState, Color, Position, GameState, GameMode } from './types';
import { INITIAL_BOARD } from './constants';
import { getValidMoves, hasLegalMoves, isCheck } from './utils/gameLogic';
import { getBestMove } from './utils/aiLogic';
import XiangqiBoard from './components/XiangqiBoard';
import TrainingPage from './components/TrainingPage';
import { RotateCcw, Undo2, Trophy, Info, Bot, User, BrainCircuit, BookOpen } from 'lucide-react';

const App: React.FC = () => {
  const [gameState, setGameState] = useState<GameState>({
    board: INITIAL_BOARD,
    turn: Color.RED,
    selectedPos: null,
    lastMove: null,
    winner: null,
    inCheck: false,
    history: [],
    gameMode: GameMode.PVP,
  });

  const [validMoves, setValidMoves] = useState<Position[]>([]);
  const [isAiThinking, setIsAiThinking] = useState(false);

  // Sound effects (using simple browser AudioContext oscillators could be an option, but keeping it silent/visual for now to avoid complexity)

  // AI Move Effect
  // AI Move Effect
  useEffect(() => {
    if (gameState.gameMode === GameMode.PVE &&
      gameState.turn === Color.BLACK &&
      !gameState.winner) {

      setIsAiThinking(true);

      const makeAiMove = async () => {
        try {
          // 1. Prepare payload
          const backendBoard = gameState.board.map(row => row.map(cell => {
            if (!cell) return 0;
            let typeInfo = 0;
            switch (cell.type) {
              case 'general': typeInfo = 1; break;
              case 'advisor': typeInfo = 2; break;
              case 'elephant': typeInfo = 3; break;
              case 'horse': typeInfo = 4; break;
              case 'chariot': typeInfo = 5; break;
              case 'cannon': typeInfo = 6; break;
              case 'soldier': typeInfo = 7; break;
            }
            return cell.color === Color.RED ? typeInfo : -typeInfo;
          }));

          // 2. Call Backend
          const response = await fetch('http://localhost:8000/bot/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ board: backendBoard, player: -1 }) // Black turn
          });

          if (!response.ok) throw new Error('Backend failed');

          const data = await response.json();
          // data.start = [x, y], data.end = [x, y]
          // Backend x=col, y=row.

          const from = { row: data.start[1], col: data.start[0] };
          const to = { row: data.end[1], col: data.end[0] };

          executeMove(from, to);

        } catch (err) {
          console.warn("AlphaZero backend unavailable, falling back to local AI:", err);
          // Fallback to local AI
          const bestMove = getBestMove(gameState.board, Color.BLACK);
          if (bestMove) {
            executeMove(bestMove.from, bestMove.to);
          }
        } finally {
          setIsAiThinking(false);
        }
      };

      // Delay slightly for UX
      const timer = setTimeout(() => {
        makeAiMove();
      }, 500);

      return () => clearTimeout(timer);
    }
  }, [gameState.turn, gameState.gameMode, gameState.winner, gameState.board]);


  // Handlers
  const handleSquareClick = (pos: Position) => {
    // Prevent interaction if game over or AI is thinking
    if (gameState.winner || isAiThinking) return;

    // Prevent human from moving AI pieces in PVE
    if (gameState.gameMode === GameMode.PVE && gameState.turn === Color.BLACK) return;

    const { board, turn, selectedPos } = gameState;
    const clickedPiece = board[pos.row][pos.col];

    // 1. If logic waiting for move target
    if (selectedPos) {
      // Check if clicking same piece -> deselect
      if (selectedPos.row === pos.row && selectedPos.col === pos.col) {
        setGameState(prev => ({ ...prev, selectedPos: null }));
        setValidMoves([]);
        return;
      }

      // Check if valid move
      const isMove = validMoves.some(m => m.row === pos.row && m.col === pos.col);

      if (isMove) {
        executeMove(selectedPos, pos);
        return;
      }

      // If clicked own piece, switch selection
      if (clickedPiece && clickedPiece.color === turn) {
        const moves = getValidMoves(board, pos);
        setGameState(prev => ({ ...prev, selectedPos: pos }));
        setValidMoves(moves);
        return;
      }

      // Clicked empty or enemy but not valid move -> Deselect
      setGameState(prev => ({ ...prev, selectedPos: null }));
      setValidMoves([]);
    } else {
      // 2. No selection yet
      if (clickedPiece && clickedPiece.color === turn) {
        const moves = getValidMoves(board, pos);
        setGameState(prev => ({ ...prev, selectedPos: pos }));
        setValidMoves(moves);
      }
    }
  };

  const executeMove = (from: Position, to: Position) => {
    // Note: We use functional state update in handleSquareClick, but here we need current state
    // We pass data around or rely on the fact that executeMove is called with valid data.

    setGameState(prevState => {
      const { board, turn, history } = prevState;

      // Create new board
      const newBoard = board.map(row => row.map(p => p ? { ...p } : null));
      newBoard[to.row][to.col] = newBoard[from.row][from.col];
      newBoard[from.row][from.col] = null;

      // Switch turn
      const nextTurn = turn === Color.RED ? Color.BLACK : Color.RED;

      // Check win condition (stalemate/checkmate)
      const opponentHasMoves = hasLegalMoves(newBoard, nextTurn);
      let winner = null;
      if (!opponentHasMoves) {
        winner = turn;
      }

      const checkStatus = isCheck(newBoard, nextTurn);

      // Save history
      const newHistory = [...history, board];

      return {
        ...prevState,
        board: newBoard,
        turn: nextTurn,
        selectedPos: null,
        lastMove: { from, to },
        winner,
        inCheck: checkStatus,
        history: newHistory,
      };
    });
    setValidMoves([]);
  };

  const handleUndo = () => {
    if (gameState.history.length === 0 || gameState.winner || isAiThinking) return;

    let stepsToUndo = 1;
    // In PvE, undoing 1 step puts you on AI turn, which might immediately trigger AI again or be weird.
    // Usually in PvE you want to undo 2 steps (Your move + AI move) to get back to your turn.
    if (gameState.gameMode === GameMode.PVE) {
      // If it's Red's turn (User), AI just moved. Undo 2.
      // If it's Black's turn (AI), User just moved. Undo 1. (But AI triggers immediately, so this state is rare unless we catch it mid-timeout)
      if (gameState.turn === Color.RED && gameState.history.length >= 2) {
        stepsToUndo = 2;
      }
    }

    setGameState(prev => {
      if (prev.history.length < stepsToUndo) return prev;

      const targetHistoryIndex = prev.history.length - stepsToUndo;
      const prevBoard = prev.history[targetHistoryIndex];
      // If we undo 2 steps, turn remains same. If 1 step, turn flips.
      const prevTurn = stepsToUndo % 2 === 0 ? prev.turn : (prev.turn === Color.RED ? Color.BLACK : Color.RED);

      return {
        ...prev,
        board: prevBoard,
        turn: prevTurn,
        history: prev.history.slice(0, targetHistoryIndex),
        selectedPos: null,
        lastMove: null,
        winner: null,
        inCheck: isCheck(prevBoard, prevTurn),
      };
    });
    setValidMoves([]);
  };

  const handleRestart = () => {
    setGameState(prev => ({
      board: INITIAL_BOARD,
      turn: Color.RED,
      selectedPos: null,
      lastMove: null,
      winner: null,
      inCheck: false,
      history: [],
      gameMode: prev.gameMode, // Keep current mode
    }));
    setValidMoves([]);
  };

  const toggleMode = (mode: GameMode) => {
    if (gameState.gameMode === mode) return;
    setGameState({
      board: INITIAL_BOARD,
      turn: Color.RED,
      selectedPos: null,
      lastMove: null,
      winner: null,
      inCheck: false,
      history: [],
      gameMode: mode,
    });
    setValidMoves([]);
  };

  return (
    <div className="min-h-screen bg-stone-100 flex flex-col items-center py-6 px-2 font-serif text-stone-900">

      {/* Header */}
      <header className="mb-6 text-center">
        <h1 className="text-4xl font-bold mb-2 text-[#8b5a2b] tracking-wider">中國象棋</h1>
        <p className="text-stone-600 flex items-center justify-center gap-2">
          React Xiangqi
          {gameState.gameMode === GameMode.PVE && <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full border border-blue-200">AI Enabled</span>}
        </p>
      </header>

      {/* Main Game Area */}
      <div className="flex flex-col lg:flex-row gap-8 items-start justify-center w-full max-w-6xl">

        {/* Left Panel: Status & Info */}
        <div className="w-full lg:w-64 space-y-4 order-2 lg:order-1">

          {/* Mode Selection */}
          <div className="bg-white p-4 rounded-xl shadow-lg border border-stone-200">
            <h2 className="text-sm font-bold text-stone-500 uppercase tracking-wide mb-3">Game Mode</h2>
            <div className="flex gap-2">
              <button
                onClick={() => toggleMode(GameMode.PVP)}
                className={`flex - 1 py - 2 px - 2 rounded - lg flex flex - col items - center gap - 1 text - sm transition - colors ${gameState.gameMode === GameMode.PVP ? 'bg-[#8b5a2b] text-white shadow-md' : 'bg-stone-100 text-stone-600 hover:bg-stone-200'} `}
              >
                <div className="flex gap-1"><User className="w-4 h-4" /><User className="w-4 h-4" /></div>
                PvP
              </button>
              <button
                onClick={() => toggleMode(GameMode.PVE)}
                className={`flex - 1 py - 2 px - 2 rounded - lg flex flex - col items - center gap - 1 text - sm transition - colors ${gameState.gameMode === GameMode.PVE ? 'bg-[#8b5a2b] text-white shadow-md' : 'bg-stone-100 text-stone-600 hover:bg-stone-200'} `}
              >
                <div className="flex gap-1"><User className="w-4 h-4" /><Bot className="w-4 h-4" /></div>
                PvE (AI)
              </button>
              <button
                onClick={() => toggleMode(GameMode.TRAINING)}
                className={`flex - 1 py - 2 px - 2 rounded - lg flex flex - col items - center gap - 1 text - sm transition - colors ${gameState.gameMode === GameMode.TRAINING ? 'bg-[#8b5a2b] text-white shadow-md' : 'bg-stone-100 text-stone-600 hover:bg-stone-200'} `}
              >
                <div className="flex gap-1"><BookOpen className="w-4 h-4" /></div>
                Training
              </button>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-lg border border-stone-200">
            <h2 className="text-xl font-bold border-b border-stone-200 pb-2 mb-4">Game Status</h2>

            {gameState.winner ? (
              <div className="flex flex-col items-center p-4 bg-yellow-50 border border-yellow-200 rounded-lg animate-bounce">
                <Trophy className="w-8 h-8 text-yellow-600 mb-2" />
                <span className="font-bold text-lg text-yellow-800">
                  {gameState.winner === Color.RED ? 'Red Wins!' : 'Black Wins!'}
                </span>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="flex items-center justify-between bg-stone-50 p-3 rounded-lg">
                  <span className="text-stone-600">Current Turn:</span>
                  <span className={`font - bold px - 3 py - 1 rounded - full flex items - center gap - 2 ${gameState.turn === Color.RED ? 'bg-red-100 text-red-700' : 'bg-gray-800 text-white'} `}>
                    {gameState.turn === Color.RED ? 'Red (帥)' : 'Black (將)'}
                    {isAiThinking && <BrainCircuit className="w-4 h-4 animate-pulse" />}
                  </span>
                </div>
                {isAiThinking && (
                  <div className="text-xs text-center text-stone-500 animate-pulse italic">
                    Computer is thinking...
                  </div>
                )}
              </div>
            )}

            {gameState.inCheck && !gameState.winner && (
              <div className="mt-4 p-3 bg-red-100 text-red-800 rounded-lg text-center font-bold border border-red-200 animate-pulse">
                CHECK!
              </div>
            )}
          </div>

          <div className="space-y-3">
            <button
              onClick={handleUndo}
              disabled={gameState.history.length === 0 || !!gameState.winner || isAiThinking}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-stone-200 hover:bg-stone-300 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors font-medium text-stone-700"
            >
              <Undo2 className="w-4 h-4" /> Undo Move
            </button>
            <button
              onClick={handleRestart}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-[#8b5a2b] hover:bg-[#704822] text-white rounded-lg transition-colors font-medium shadow-md"
            >
              <RotateCcw className="w-4 h-4" /> Restart Game
            </button>
          </div>

          <div className="mt-4 text-sm text-stone-500">
            <div className="flex items-center gap-2 mb-2 font-bold text-stone-700">
              <Info className="w-4 h-4" /> Rules
            </div>
            <ul className="list-disc list-inside space-y-1">
              <li>Red moves first.</li>
              <li>Generals can't face each other.</li>
              <li>Standard Xiangqi rules.</li>
            </ul>
          </div>
        </div>

        {/* Center: The Board or Training Page */}
        <div className="flex-grow flex justify-center order-1 lg:order-2 w-full">
          {gameState.gameMode === GameMode.TRAINING ? (
            <TrainingPage />
          ) : (
            <XiangqiBoard
              board={gameState.board}
              turn={gameState.turn}
              selectedPos={gameState.selectedPos}
              validMoves={validMoves}
              lastMove={gameState.lastMove}
              onSquareClick={handleSquareClick}
              winner={gameState.winner}
            />
          )}
        </div>

        {/* Right Panel: Captured / Graveyard (Optional - placeholder for visual balance) */}
        <div className="hidden lg:block w-64 order-3">
          {/* Could add captured pieces list here for visual completeness */}
        </div>

      </div>

      <footer className="mt-12 text-stone-400 text-sm">
        <p>Built with React & Tailwind</p>
      </footer>
    </div>
  );
};

export default App;