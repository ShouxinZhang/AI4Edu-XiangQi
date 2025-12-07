"""
Prediction Server for Batched GPU Inference.

Collects inference requests from multiple workers and batches them
for efficient GPU utilization.
"""
import torch
import numpy as np
from multiprocessing import Queue
import time
import threading


class PredictionServer:
    """
    A server that batches inference requests from multiple workers
    and sends results back.
    """
    
    def __init__(self, model, game, batch_size: int = 32, timeout: float = 0.05):
        """
        Initialize prediction server.
        
        Args:
            model: Neural network model
            game: Game instance
            batch_size: Maximum batch size for inference
            timeout: Maximum time to wait for more requests
        """
        self.model = model
        self.game = game
        self.batch_size = batch_size
        self.timeout = timeout
        self.running = False
        
        # Queues for communication
        self.request_queue = Queue()
        self.response_queues = {}
        
    def start(self):
        """Start the prediction server in a background thread."""
        self.running = True
        self.thread = threading.Thread(target=self._serve_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop the prediction server."""
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1.0)
            
    def register_worker(self, worker_id):
        """
        Register a worker and return its response queue.
        
        Args:
            worker_id: Unique worker identifier
            
        Returns:
            Response queue for this worker
        """
        response_queue = Queue()
        self.response_queues[worker_id] = response_queue
        return response_queue
        
    def predict(self, worker_id, board_tensor):
        """
        Submit a prediction request and wait for result.
        Called by workers.
        
        Args:
            worker_id: Worker identifier
            board_tensor: Board state tensor
            
        Returns:
            Tuple of (policy, value)
        """
        self.request_queue.put((worker_id, board_tensor))
        response_queue = self.response_queues[worker_id]
        return response_queue.get()
        
    def _serve_loop(self):
        """Main loop: collect requests, batch, infer, distribute."""
        while self.running:
            requests = []
            start_time = time.time()
            
            # Collect requests until batch full or timeout
            while len(requests) < self.batch_size:
                elapsed = time.time() - start_time
                remaining = self.timeout - elapsed
                
                if remaining <= 0:
                    break
                    
                try:
                    # Non-blocking with timeout
                    req = self.request_queue.get(timeout=remaining)
                    requests.append(req)
                except:
                    break
                    
            if not requests:
                continue
                
            # Batch inference
            worker_ids = [r[0] for r in requests]
            tensors = [r[1] for r in requests]
            
            batch = np.stack(tensors)
            batch_tensor = torch.FloatTensor(batch)
            
            if next(self.model.parameters()).is_cuda:
                batch_tensor = batch_tensor.cuda()
                
            with torch.no_grad():
                policies, values = self.model(batch_tensor)
                policies = policies.cpu().numpy()
                values = values.cpu().numpy()
                
            # Distribute results
            for i, worker_id in enumerate(worker_ids):
                result = (policies[i], values[i][0])
                if worker_id in self.response_queues:
                    self.response_queues[worker_id].put(result)


class PredictionClient:
    """
    Client for workers to send prediction requests.
    """
    
    def __init__(self, request_queue, response_queue):
        """
        Initialize client.
        
        Args:
            request_queue: Queue to send requests
            response_queue: Queue to receive responses
        """
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.worker_id = id(self)
        
    def predict(self, board_tensor):
        """
        Send a prediction request and wait for result.
        
        Args:
            board_tensor: Board state tensor
            
        Returns:
            Tuple of (policy, value)
        """
        self.request_queue.put((self.worker_id, board_tensor))
        return self.response_queue.get()
