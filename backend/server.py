"""
Main FastAPI server - Minimal entry point.
Routes are organized in routers/ directory.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import psutil

from routers import game_router, training_router

app = FastAPI(title="AI4Edu Xiangqi API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(game_router)
app.include_router(training_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/api/gpu/stats")
def get_gpu_stats():
    """Get GPU utilization stats."""
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
    """Get CPU and memory stats."""
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
