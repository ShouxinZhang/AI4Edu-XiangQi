
import asyncio
import websockets
import requests
import json
import time
import threading
import sys
import uvicorn
from server import app

# Function to run server in a thread
def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")

async def test_ws():
    uri = "ws://localhost:8001/ws/training"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket")
        
        # Send update via REST in a separate thread/process style (or just here since it's async)
        # But requests is blocking.
        # simpler: just make the request using requests
        update_data = {
            "type": "step",
            "data": {
                "board": [[0]*9]*10,
                "step": 123
            }
        }
        
        print("Sending POST request...")
        # We need to run this in a non-blocking way or start server first.
        # Since server is in a thread, we can just call requests.
        response = requests.post("http://localhost:8001/internal/training/update", json=update_data)
        print(f"POST response: {response.status_code}")
        
        # Wait for WS message
        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
        print(f"Received WS message: {message}")
        
        received = json.loads(message)
        assert received["type"] == "step"
        assert received["data"]["step"] == 123
        print("Verification PASSED!")

if __name__ == "__main__":
    # Start server in thread
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(2) # Wait for server startup
    
    # Run async test
    try:
        asyncio.run(test_ws())
    except Exception as e:
        print(f"Verification FAILED: {e}")
        sys.exit(1)
