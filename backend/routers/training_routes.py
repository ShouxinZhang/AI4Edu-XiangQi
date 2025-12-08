"""
Training-related API routes: status, control, configuration.
"""
import os
import json
import signal
import subprocess

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.websocket_manager import manager
from schemas.game_schemas import TrainingUpdate, TrainingStartRequest
from history import HistoryManager

router = APIRouter()

history_manager = HistoryManager()

# Shared training state (in-memory)
training_state = {
    "iteration": 0,
    "episode": 0,
    "total_episodes": 0,
    "step": 0,
    "games_completed": 0,
    "status": "idle",
    "history": [],
    "evalHistory": []
}

# Global training process reference
training_process = None
training_config = {
    "max_steps": 200,
    "workers": 4,
    "mode": "parallel",
    "num_mcts_sims": 25
}


@router.websocket("/ws/training")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time training updates."""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post("/internal/training/update")
async def training_update(update: TrainingUpdate):
    """Broadcast training update to WebSocket clients."""
    await manager.broadcast(update.dict())
    return {"status": "broadcasted"}


@router.post("/internal/training/state")
async def update_training_state(state: dict):
    """Update training state from worker processes."""
    global training_state

    if "history_update" in state:
        item = state.pop("history_update")
        history_manager.save_game(item, mode="training")

    training_state.update(state)
    training_state["history"] = history_manager.get_recent_history(mode="training", limit=50)

    return {"status": "ok"}


@router.post("/internal/training/step")
async def update_training_step(step_data: dict):
    """Receive real-time step updates from workers."""
    await manager.broadcast({
        "type": "step",
        "data": {
            "worker_id": step_data.get("worker_id", 0),
            "step": step_data.get("step", 0),
            "board": step_data.get("board"),
            "player": step_data.get("player", 1)
        }
    })
    return {"status": "ok"}


@router.get("/api/training/state")
def get_training_state():
    """Get current training state."""
    return training_state


@router.post("/api/training/start")
async def start_training(config: TrainingStartRequest = None):
    """Start training process with given configuration."""
    global training_process, training_config, training_state

    if training_process and training_process.poll() is None:
        return {"status": "error", "message": "Training already running. Stop it first."}

    if config:
        training_config["max_steps"] = config.max_steps
        training_config["workers"] = config.workers
        training_config["mode"] = config.mode
        training_config["num_mcts_sims"] = config.num_mcts_sims
        training_config["num_episodes"] = config.num_episodes

    cmd = ["python", "-m", "rl.train", "--mode", training_config["mode"],
           "--max-steps", str(training_config["max_steps"]),
           "--num-mcts-sims", str(training_config["num_mcts_sims"]),
           "--num-episodes", str(training_config.get("num_episodes", 10))]
    
    if training_config["mode"] == "parallel":
        cmd.extend(["--workers", str(training_config["workers"])])

    log_file = open("/tmp/training_process.log", "w")
    training_process = subprocess.Popen(
        cmd,
        cwd="/home/wudizhe001/Documents/GitHub/AI4Edu-XiangQi/backend",
        stdout=log_file,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid
    )

    training_state["status"] = "starting"
    training_state["iteration"] = 0
    training_state["episode"] = 0
    training_state["total_episodes"] = training_config.get("num_episodes", 10)

    return {
        "status": "ok",
        "message": f"Training started in {training_config['mode']} mode",
        "pid": training_process.pid,
        "config": training_config
    }


@router.post("/api/training/stop")
async def stop_training():
    """Stop the current training process."""
    global training_process, training_state

    stopped = False

    if training_process is not None and training_process.poll() is None:
        try:
            os.killpg(os.getpgid(training_process.pid), signal.SIGTERM)
            training_process.wait(timeout=5)
            stopped = True
        except Exception:
            try:
                os.killpg(os.getpgid(training_process.pid), signal.SIGKILL)
                stopped = True
            except:
                pass
        training_process = None

    try:
        result = subprocess.run(["pkill", "-9", "-f", "rl.train"], capture_output=True)
        if result.returncode == 0:
            stopped = True
    except:
        pass

    training_state["status"] = "stopped"

    return {"status": "ok", "message": "Training stopped" if stopped else "No training process found"}


@router.post("/api/training/reset")
async def reset_training():
    """Stop training and clear all training data."""
    global training_state

    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(base_dir)  # Go up from routers to backend

    await stop_training()

    deleted_counts = {"checkpoints": 0, "evolution": 0, "history": 0}

    # Clear Checkpoints
    try:
        checkpoint_dir = os.path.join(base_dir, "checkpoints")
        if os.path.exists(checkpoint_dir):
            for f in os.listdir(checkpoint_dir):
                if f.endswith(".pth.tar"):
                    os.remove(os.path.join(checkpoint_dir, f))
                    deleted_counts["checkpoints"] += 1
    except Exception as e:
        print(f"Error clearing checkpoints: {e}")

    # Clear Evolution Data
    try:
        evolution_dir = os.path.join(base_dir, "data", "evolution")
        if os.path.exists(evolution_dir):
            for f in os.listdir(evolution_dir):
                if f.endswith(".json"):
                    os.remove(os.path.join(evolution_dir, f))
                    deleted_counts["evolution"] += 1
    except Exception as e:
        print(f"Error clearing evolution data: {e}")

    # Clear Training History
    try:
        history_file = os.path.join(base_dir, "data", "history", "training_games.jsonl")
        if os.path.exists(history_file):
            os.remove(history_file)
            deleted_counts["history"] = 1
    except Exception as e:
        print(f"Error clearing history: {e}")

    # Reset Training State
    training_state = {
        "iteration": 0,
        "episode": 0,
        "total_episodes": 0,
        "step": 0,
        "games_completed": 0,
        "status": "idle",
        "history": [],
        "evalHistory": []
    }

    print(f"[Reset] Deleted: {deleted_counts}")
    return {"status": "ok", "message": f"Training data cleared. Deleted: {deleted_counts}"}


@router.get("/api/training/config")
async def get_training_config_api():
    """Get current training configuration."""
    global training_process, training_config, training_state

    config_file = "data/training_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                saved_config = json.load(f)
                training_config.update(saved_config)
        except:
            pass

    api_process_running = training_process is not None and training_process.poll() is None
    state_indicates_running = training_state.get("status") not in ["idle", "stopped", None, ""]
    is_running = api_process_running or state_indicates_running

    return {
        "config": training_config,
        "is_running": is_running,
        "pid": training_process.pid if api_process_running else None,
        "status": training_state.get("status", "idle")
    }


@router.post("/api/training/config")
async def save_training_config_api(config: TrainingStartRequest):
    """Save training configuration to disk."""
    global training_config

    training_config["max_steps"] = config.max_steps
    training_config["workers"] = config.workers
    training_config["mode"] = config.mode
    training_config["num_mcts_sims"] = config.num_mcts_sims

    config_file = "data/training_config.json"
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, 'w') as f:
        json.dump(training_config, f, indent=2)

    return {"status": "ok", "message": "Configuration saved", "config": training_config}
