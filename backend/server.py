from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import numpy as np
from typing import List, Tuple
import json
import subprocess

from game import XiangqiGame, BOARD_HEIGHT, BOARD_WIDTH
from rl.models.xiangqi_net import XiangqiNet
from rl.algorithms.mcts import MCTS
from history import HistoryManager
from classic.minimax import MinimaxSolver
from typing import Optional

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared training state (simple in-memory, updated by train.py via POST)
training_state = {
    "iteration": 0,
    "episode": 0,
    "total_episodes": 0,
    "step": 0,
    "games_completed": 0,
    "status": "idle",
    "history": [], # List of { id, winner, steps, timestamp }
    "evalHistory": [] # List of {iteration, vsLevel1, vsLevel2, vsLevel3}
}

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"[WS] Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        print(f"[WS] Broadcasting to {len(self.active_connections)} clients...")
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"[WS] Error sending to client: {e}")
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

class BoardRequest(BaseModel):
    board: List[List[int]]
    player: int # 1 for Red, -1 for Black
    difficulty: Optional[int] = None # 1-4 Classic, None for AlphaZero

class MoveResponse(BaseModel):
    start: Tuple[int, int]
    end: Tuple[int, int]

# Global variables
game = XiangqiGame()
nnet = XiangqiNet()
history_manager = HistoryManager()
args = {
    'num_mcts_sims': 50,
    'cpuct': 1.0,
    'cuda': torch.cuda.is_available()
}

if args['cuda']:
    nnet.cuda()

# Load checkpoint if exists, else random
try:
    checkpoint = torch.load('checkpoints/checkpoint_best.pth.tar')
    nnet.load_state_dict(checkpoint['state_dict'])
    print("Loaded best model.")
except:
    print("No checkpoint found, using random model.")
    pass

nnet.eval()

@app.post("/bot/move", response_model=MoveResponse)
@app.post("/api/ai/move", response_model=MoveResponse)
async def get_bot_move(req: BoardRequest):
    # Reconstruct game state
    # We assume the board sent is in "Absolute Coordinates"
    # Player passed is whose turn it is.
    
    current_board = np.array(req.board)
    current_player = req.player
    
    # MCTS expects canonical board
    canonical_board = game.get_canonical_form(current_board, current_player)
    
    action = None
    
    # Default to AlphaZero if no difficulty or difficulty invalid
    if req.difficulty and 1 <= req.difficulty <= 4:
        # Use Classic Minimax
        # Level 1=D1, 2=D2, 3=D3, 4=D4
        solver = MinimaxSolver(game, depth=req.difficulty)
        action = solver.get_best_move(canonical_board)
    else:
        # Run AlphaZero (MCTS)
        # Create a fresh MCTS for this request (stateless for now)
        mcts = MCTS(game, nnet, args)
        
        # Get action probabilities (temp=0 for competitive play)
        pi = mcts.get_action_prob(canonical_board, temp=0)
        
        # Choose action
        action = np.argmax(pi)
    
    # Decode action (in Canonical Board coordinates)
    move = game.decode_move(action)
    start, end = move
    
    # Convert from Canonical to Absolute coordinates
    # If current_player is Black (-1), canonical board was flipped (flipud)
    # So we need to flip y-coordinates back: y -> 9 - y
    if current_player == -1:
        start = (start[0], 9 - start[1])
        end = (end[0], 9 - end[1])
    
    return {"start": start, "end": end}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.websocket("/ws/training")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

class TrainingUpdate(BaseModel):
    type: str # 'step' or 'game_end'
    data: dict

@app.post("/internal/training/update")
async def training_update(update: TrainingUpdate):
    await manager.broadcast(update.dict())
    return {"status": "broadcasted"}

@app.post("/internal/training/state")
async def update_training_state(state: dict):
    global training_state
    
    if "history_update" in state:
        item = state.pop("history_update")
        # Save to persistent storage
        history_manager.save_game(item, mode="training")
            
    training_state.update(state)
    
    # Inject recent history back into state for WebSocket broadcast (so frontend updates immediately)
    # Optimization: Only send top 5 to keep packet small? 
    # Or just let frontend fetch full history via API?
    # Current frontend expects "history" in state for WebSocket updates.
    # Let's populate it from memory or storage.
    training_state["history"] = history_manager.get_recent_history(mode="training", limit=50)
    
    return {"status": "ok"}

@app.get("/api/training/state")
def get_training_state():
    return training_state

# Add API to fetch persistent history
@app.get("/api/history")
async def get_history(mode: str = "training"):
    return history_manager.get_recent_history(mode=mode)

class SaveGameRequest(BaseModel):
    mode: str  # 'pvp', 'pve', 'training'
    winner: int  # 1 = Red, -1 = Black, 0 = Draw
    moves: list  # List of moves [[from, to], ...]
    timestamp: float = None

@app.post("/api/games/save")
async def save_game(req: SaveGameRequest):
    import uuid
    game_data = {
        "game_id": str(uuid.uuid4()),
        "winner": req.winner,
        "moves": req.moves,
        "timestamp": req.timestamp or time.time(),
    }
    history_manager.save_game(game_data, mode=req.mode)
    return {"status": "ok", "game_id": game_data["game_id"]}

@app.get("/api/gpu/stats")
def get_gpu_stats():
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        parts = result.stdout.strip().split(",")
        return {
            "gpu_utilization": int(parts[0].strip()),
            "memory_used_mb": int(parts[1].strip()),
            "memory_total_mb": int(parts[2].strip()),
            "temperature_c": int(parts[3].strip())
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/cpu/stats")
def get_cpu_stats():
    import psutil
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        return {
            "cpu_utilization": cpu_percent,
            "memory_used_mb": memory.used // (1024 * 1024),
            "memory_total_mb": memory.total // (1024 * 1024),
            "memory_percent": memory.percent
        }
    except Exception as e:
        return {"error": str(e)}

# ========== Evolution API for RL Training Games ==========
import os
import glob

def load_evolution_games(iteration: int = None, limit: int = 50):
    """Load RL training games from data/evolution directory."""
    evolution_dir = "data/evolution"
    games = []
    
    if not os.path.exists(evolution_dir):
        return []
    
    # Scan for game files
    pattern = f"game_{iteration}_*.json" if iteration else "game_*.json"
    files = glob.glob(os.path.join(evolution_dir, pattern))
    
    # Sort by modification time (newest first)
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
            # Extract iteration from filename: game_{iter}_{uuid}.json
            parts = filename.split("_")
            if len(parts) >= 2:
                try:
                    iterations.add(int(parts[1]))
                except ValueError:
                    pass
    
    return sorted(iterations, reverse=True)

@app.get("/api/evolution/games")
async def get_evolution_games(iteration: int = None, limit: int = 50):
    """Get RL training games, optionally filtered by iteration."""
    return load_evolution_games(iteration, limit)

@app.get("/api/evolution/iterations")
async def get_evolution_iterations():
    """Get list of available training iterations."""
    return get_available_iterations()


# ========== Training Control API ==========
import signal

# Global training process reference
training_process = None
training_config = {
    "max_steps": 200,
    "workers": 4,
    "mode": "parallel",  # "single" or "parallel"
    "num_mcts_sims": 25
}

class TrainingStartRequest(BaseModel):
    max_steps: int = 200
    workers: int = 4
    mode: str = "parallel"  # "single" or "parallel"
    num_mcts_sims: int = 25

@app.post("/api/training/start")
async def start_training(config: TrainingStartRequest = None):
    """Start training process with given configuration."""
    global training_process, training_config, training_state
    
    # Stop existing process if running
    if training_process and training_process.poll() is None:
        return {"status": "error", "message": "Training already running. Stop it first."}
    
    # Update config
    if config:
        training_config["max_steps"] = config.max_steps
        training_config["workers"] = config.workers
        training_config["mode"] = config.mode
        training_config["num_mcts_sims"] = config.num_mcts_sims
    
    # Build command
    cmd = ["python", "-m", "rl.train", "--mode", training_config["mode"]]
    if training_config["mode"] == "parallel":
        cmd.extend(["--workers", str(training_config["workers"])])
    
    # Start training process
    training_process = subprocess.Popen(
        cmd,
        cwd="/home/wudizhe001/Documents/GitHub/AI4Edu-XiangQi/backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid  # Create new process group for clean termination
    )
    
    training_state["status"] = "starting"
    training_state["iteration"] = 0
    
    return {
        "status": "ok",
        "message": f"Training started in {training_config['mode']} mode",
        "pid": training_process.pid,
        "config": training_config
    }

@app.post("/api/training/stop")
async def stop_training():
    """Stop the current training process."""
    global training_process, training_state
    
    if training_process is None:
        return {"status": "error", "message": "No training process running"}
    
    if training_process.poll() is not None:
        training_process = None
        return {"status": "error", "message": "Training process already stopped"}
    
    try:
        # Kill the entire process group
        os.killpg(os.getpgid(training_process.pid), signal.SIGTERM)
        training_process.wait(timeout=5)
    except Exception as e:
        # Force kill if SIGTERM fails
        try:
            os.killpg(os.getpgid(training_process.pid), signal.SIGKILL)
        except:
            pass
    
    training_process = None
    training_state["status"] = "stopped"
    
    return {"status": "ok", "message": "Training stopped"}

@app.get("/api/training/config")
async def get_training_config_api():
    """Get current training configuration."""
    global training_process, training_config, training_state
    
    # Load saved config if exists
    config_file = "data/training_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                saved_config = json.load(f)
                training_config.update(saved_config)
        except:
            pass
    
    # Check if running: either via API process or via training_state status
    api_process_running = training_process is not None and training_process.poll() is None
    state_indicates_running = training_state.get("status") not in ["idle", "stopped", None, ""]
    is_running = api_process_running or state_indicates_running
    
    return {
        "config": training_config,
        "is_running": is_running,
        "pid": training_process.pid if api_process_running else None,
        "status": training_state.get("status", "idle")
    }

@app.post("/api/training/config")
async def save_training_config_api(config: TrainingStartRequest):
    """Save training configuration to disk."""
    global training_config
    
    training_config["max_steps"] = config.max_steps
    training_config["workers"] = config.workers
    training_config["mode"] = config.mode
    training_config["num_mcts_sims"] = config.num_mcts_sims
    
    # Save to file
    config_file = "data/training_config.json"
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, 'w') as f:
        json.dump(training_config, f, indent=2)
    
    return {"status": "ok", "message": "Configuration saved", "config": training_config}

