from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import numpy as np
from typing import List, Tuple
import json
import subprocess

from game import XiangqiGame, BOARD_HEIGHT, BOARD_WIDTH
from model import XiangqiNet
from mcts import MCTS

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
    "history": [] # List of { id, winner, steps, timestamp }
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

class MoveResponse(BaseModel):
    start: Tuple[int, int]
    end: Tuple[int, int]

# Global variables
game = XiangqiGame()
nnet = XiangqiNet()
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
async def get_bot_move(req: BoardRequest):
    # Reconstruct game state
    # We assume the board sent is in "Absolute Coordinates"
    # Player passed is whose turn it is.
    
    current_board = np.array(req.board)
    current_player = req.player
    
    # MCTS expects canonical board
    canonical_board = game.get_canonical_form(current_board, current_player)
    
    # Run MCTS
    # Create a fresh MCTS for this request (stateless for now)
    # In production, we might want to keep the tree if we can track state, 
    # but for a simple REST API, stateless is easier.
    mcts = MCTS(game, nnet, args)
    
    # Get action probabilities (temp=0 for competitive play)
    pi = mcts.get_action_prob(canonical_board, temp=0)
    
    # Choose action
    action = np.argmax(pi)
    
    # Decode action
    move = game.decode_move(action)
    start, end = move
    
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
        # Prepend to history (newest first), keep last 50
        training_state["history"].insert(0, item)
        if len(training_state["history"]) > 50:
            training_state["history"].pop()
            
    training_state.update(state)
    return {"status": "ok"}

@app.get("/api/training/state")
def get_training_state():
    return training_state

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
