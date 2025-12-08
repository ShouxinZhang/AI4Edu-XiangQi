"""
Game-related API routes: AI move, game saving, evolution data.
"""
import json
import time
import threading
import queue
import os
import glob

import numpy as np
import torch
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from game import XiangqiGame
from classic.minimax import MinimaxSolver
from rl.models.xiangqi_net import XiangqiNet
from rl.algorithms.mcts import MCTS
from history import HistoryManager
from schemas.game_schemas import BoardRequest, SaveGameRequest

router = APIRouter()

# Initialize game and AI components
game = XiangqiGame()
nnet = XiangqiNet()
history_manager = HistoryManager()

# Global abort event for Minimax interruption
current_abort_event = None

# MCTS args
args = {
    'num_mcts_sims': 50,
    'cpuct': 1.0,
    'cuda': torch.cuda.is_available()
}

if args['cuda']:
    nnet.cuda()

# Load checkpoint if exists
try:
    checkpoint = torch.load('checkpoints/checkpoint_best.pth.tar')
    nnet.load_state_dict(checkpoint['state_dict'])
    print("Loaded best model.")
except:
    print("No checkpoint found, using random model.")

nnet.eval()


@router.post("/bot/move")
@router.post("/api/ai/move")
async def get_bot_move(req: BoardRequest):
    """Get AI move with streaming progress updates."""
    current_board = np.array(req.board)
    current_player = req.player
    canonical_board = game.get_canonical_form(current_board, current_player)

    async def move_generator():
        global current_abort_event

        # Signal any existing calculation to stop
        if current_abort_event is not None:
            print("[Server] Stopping previous calculation...")
            current_abort_event.set()

        # Create new abort event for this request
        my_abort_event = threading.Event()
        current_abort_event = my_abort_event
        start_time = time.time()

        if req.difficulty and 1 <= req.difficulty <= 20:
            # Classic Minimax with streaming progress
            q = queue.Queue()

            def worker(abort_event):
                def cb(c, t):
                    if abort_event.is_set():
                        return
                    q.put(("progress", c, t))

                def abort_check():
                    return abort_event.is_set()

                solver = MinimaxSolver(game, depth=req.difficulty)
                try:
                    action = solver.get_best_move(canonical_board, progress_callback=cb, abort_check=abort_check)
                    if abort_event.is_set():
                        q.put(("aborted",))
                    else:
                        q.put(("result", action))
                except Exception as e:
                    print(f"Solver Error: {e}")
                    q.put(("error", str(e)))

            t = threading.Thread(target=worker, args=(my_abort_event,))
            t.start()

            while True:
                if my_abort_event.is_set():
                    print("[Server] Move calculation aborted.")
                    break

                try:
                    item = q.get(timeout=0.05)

                    if item[0] == "progress":
                        c, total = item[1], item[2]
                        now = time.time()
                        percent = (c / total) if total > 0 else 0
                        elapsed = now - start_time
                        eta = (elapsed / percent) - elapsed if percent > 0.01 else 0

                        yield json.dumps({
                            "type": "progress",
                            "percent": round(percent * 100, 1),
                            "eta_seconds": round(eta, 1)
                        }) + "\n"

                    elif item[0] == "result":
                        action = item[1]
                        if action is not None:
                            move = game.decode_move(action)
                            start, end = move
                            if current_player == -1:
                                start = (start[0], 9 - start[1])
                                end = (end[0], 9 - end[1])

                            yield json.dumps({
                                "type": "result",
                                "start": start,
                                "end": end
                            }) + "\n"
                        break

                    elif item[0] == "aborted":
                        print("[Server] Worker confirmed abort.")
                        break

                    elif item[0] == "error":
                        print(f"[Server] Worker error: {item[1]}")
                        break

                except queue.Empty:
                    if not t.is_alive():
                        break
                    continue

        else:
            # AlphaZero (MCTS)
            mcts = MCTS(game, nnet, args)
            pi = mcts.get_action_prob(canonical_board, temp=0)
            action = np.argmax(pi)

            move = game.decode_move(action)
            start, end = move
            if current_player == -1:
                start = (start[0], 9 - start[1])
                end = (end[0], 9 - end[1])

            yield json.dumps({
                "type": "result",
                "start": start,
                "end": end
            }) + "\n"

    return StreamingResponse(move_generator(), media_type="application/x-ndjson")


@router.post("/api/games/save")
async def save_game(req: SaveGameRequest):
    """Save a completed game to history."""
    import uuid
    game_data = {
        "game_id": str(uuid.uuid4()),
        "winner": req.winner,
        "moves": req.moves,
        "timestamp": req.timestamp or time.time(),
    }
    history_manager.save_game(game_data, mode=req.mode)
    return {"status": "ok", "game_id": game_data["game_id"]}


@router.get("/api/history")
async def get_history(mode: str = "training"):
    """Get recent game history."""
    return history_manager.get_recent_history(mode=mode)


# ========== Evolution API ==========

def load_evolution_games(iteration: int = None, limit: int = 50):
    """Load RL training games from data/evolution directory."""
    evolution_dir = "data/evolution"
    games = []

    if not os.path.exists(evolution_dir):
        return []

    pattern = f"game_{iteration}_*.json" if iteration else "game_*.json"
    files = glob.glob(os.path.join(evolution_dir, pattern))
    files.sort(key=os.path.getmtime, reverse=True)

    for filepath in files[:limit]:
        try:
            with open(filepath, 'r') as f:
                game_data = json.load(f)
                game_data['source'] = 'rl'
                games.append(game_data)
        except:
            pass

    return games


def get_available_iterations():
    """Get list of available iteration numbers from evolution data."""
    evolution_dir = "data/evolution"
    iterations = set()

    if not os.path.exists(evolution_dir):
        return []

    for filename in os.listdir(evolution_dir):
        if filename.startswith("game_") and filename.endswith(".json"):
            parts = filename.split("_")
            if len(parts) >= 2:
                try:
                    iterations.add(int(parts[1]))
                except ValueError:
                    pass

    return sorted(iterations, reverse=True)


@router.get("/api/evolution/games")
async def get_evolution_games(iteration: int = None, limit: int = 50):
    """Get RL training games, optionally filtered by iteration."""
    return load_evolution_games(iteration, limit)


@router.get("/api/evolution/iterations")
async def get_evolution_iterations():
    """Get list of available training iterations."""
    return get_available_iterations()
