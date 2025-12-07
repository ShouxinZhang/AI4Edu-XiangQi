"""
Broadcast Client for Training Updates.

Sends training progress updates to the server for real-time visualization.
"""
import requests
import json


class BroadcastClient:
    """
    Broadcasts training updates to the server via HTTP POST.
    
    Used to send step updates, game completions, etc. to the frontend.
    """
    
    def __init__(self, url: str = "http://localhost:8000/internal/training/update"):
        """
        Initialize broadcast client.
        
        Args:
            url: Server endpoint for training updates
        """
        self.url = url
    
    def broadcast(self, data: dict):
        """
        Send an update to the server.
        
        Args:
            data: Dict with update information
        """
        try:
            requests.post(self.url, json=data, timeout=0.5)
        except Exception:
            pass  # Non-blocking, ignore failures
