import React, { useState, useEffect } from 'react';
import { BoardState, Color, Position, GameMode } from './src/types';
import { getValidMoves, hasLegalMoves } from './utils/gameLogic';
import { getBestMove } from './utils/aiLogic';
import XiangqiBoard from './src/components/game/XiangqiBoard';
import TrainingPage from './src/components/training/TrainingPage';
import { useGame } from './src/store';
import { saveGameResult, getAIMove } from './src/api';
import ReplayPage from './src/pages/ReplayPage';

// Layout Components
import { MainLayout } from './src/components/layout/MainLayout';
import { GameControlPanel } from './src/components/layout/GameControlPanel';

const App: React.FC = () => {
  // Use global game context
  const { state: gameState, dispatch, selectPiece, makeMove, setWinner, undo, reset, setMode } = useGame();
  const [validMoves, setValidMoves] = useState<Position[]>([]);
  const [isAiThinking, setIsAiThinking] = useState(false);

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
          // 2. Call Backend using API client
          const data = await getAIMove(backendBoard, -1, gameState.difficulty);

          // data.start = [x, y], data.end = [x, y]
          // data.start = [x, y], data.end = [x, y]
          // Backend x=col, y=row.

          const from = { row: data.start[1], col: data.start[0] };
          const to = { row: data.end[1], col: data.end[0] };

          executeMove(from, to);

        } catch (err) {
          console.warn("AlphaZero backend unavailable, falling back to local AI:", err);
          // Fallback to local AI logic
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
        selectPiece(null as any);
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
        selectPiece(pos);
        setValidMoves(moves);
        return;
      }

      // Clicked empty or enemy but not valid move -> Deselect
      selectPiece(null as any);
      setValidMoves([]);
    } else {
      // 2. No selection yet
      if (clickedPiece && clickedPiece.color === turn) {
        const moves = getValidMoves(board, pos);
        selectPiece(pos);
        setValidMoves(moves);
      }
    }
  };

  const executeMove = (from: Position, to: Position) => {
    const { board, turn } = gameState;

    // Create new board
    const newBoard = board.map(row => row.map(p => p ? { ...p } : null)) as BoardState;
    newBoard[to.row][to.col] = newBoard[from.row][from.col];
    newBoard[from.row][from.col] = null;

    // Use context makeMove
    makeMove(from, to, newBoard);

    // Check win condition
    const nextTurn = turn === Color.RED ? Color.BLACK : Color.RED;
    const opponentHasMoves = hasLegalMoves(newBoard, nextTurn);
    if (!opponentHasMoves) {
      setWinner(turn);

      // Save game to history
      const winnerValue = turn === Color.RED ? 1 : -1;
      const mode = gameState.gameMode === GameMode.PVP ? 'pvp' : 'pve';
      const moves = [...gameState.history, { from, to }];
      saveGameResult(mode, winnerValue, moves).catch(err => {
        console.warn('Failed to save game:', err);
      });
    }

    setValidMoves([]);
  };

  const handleUndo = () => {
    if (gameState.history.length === 0 || gameState.winner || isAiThinking) return;
    undo();
    setValidMoves([]);
  };

  const handleRestart = () => {
    reset();
    setValidMoves([]);
  };

  const handleModeChange = (mode: GameMode) => {
    if (gameState.gameMode === mode) return;
    setMode(mode);
    setValidMoves([]);
  };

  const handleSaveGame = () => {
    if (gameState.moveHistory.length === 0) return;
    const mode = gameState.gameMode === GameMode.PVP ? 'pvp' : 'pve';
    const winner = gameState.winner ? (gameState.winner === Color.RED ? 1 : -1) : 0;
    saveGameResult(mode, winner, gameState.moveHistory).then(() => {
      alert('Game saved!');
    }).catch(err => {
      console.warn('Failed to save game:', err);
      alert('Failed to save game.');
    });
  };

  // Render Content based on Mode
  const renderContent = () => {
    if (gameState.gameMode === GameMode.REPLAY) {
      return <ReplayPage />;
    }

    if (gameState.gameMode === GameMode.TRAINING) {
      return <TrainingPage />;
    }

    // Default: PvP or PvE
    return (
      <div className="flex flex-col lg:flex-row gap-8 items-start justify-center w-full">
        {/* Main Game Board */}
        <div className="flex-grow flex justify-center order-1 lg:order-1 w-full lg:w-auto">
          <XiangqiBoard
            board={gameState.board}
            turn={gameState.turn}
            selectedPos={gameState.selectedPos}
            validMoves={validMoves}
            lastMove={gameState.lastMove}
            onSquareClick={handleSquareClick}
            winner={gameState.winner}
          />
        </div>

        {/* Right Control Panel */}
        <div className="w-full lg:w-80 order-2 lg:order-2 flex-shrink-0">
          <GameControlPanel
            turn={gameState.turn}
            winner={gameState.winner}
            inCheck={gameState.inCheck}
            isAiThinking={isAiThinking}
            onUndo={handleUndo}
            onRestart={handleRestart}
            onSave={handleSaveGame}
            canUndo={gameState.history.length > 0}
            canSave={gameState.history.length > 0}
          />
        </div>
      </div>
    );
  };

  return (
    <MainLayout currentMode={gameState.gameMode} onModeChange={handleModeChange}>
      {renderContent()}
    </MainLayout>
  );
};

export default App;