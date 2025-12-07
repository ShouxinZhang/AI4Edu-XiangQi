"""
Parallel Trainer - Multi-worker self-play with batched GPU inference.

Provides ParallelTrainer class for distributed training.
"""
import os
import numpy as np
import random
import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from multiprocessing import Process, Queue
from tqdm import tqdm
import requests

from ..workers.prediction_server import PredictionServer
from ..workers.self_play import run_worker
from .dataset import XiangqiDataset


class ParallelTrainer:
    """
    Parallel training using multiple worker processes.
    
    Uses a central prediction server for batched GPU inference
    and multiple worker processes for self-play.
    """
    
    def __init__(self, game_class, model, args):
        """
        Initialize parallel trainer.
        
        Args:
            game_class: Game class (not instance, will be instantiated in workers)
            model: Neural network model
            args: Training configuration dict
        """
        self.game_class = game_class
        self.model = model
        self.args = args
        self.train_examples_history = []
        self.start_iteration = 1

    def parallel_self_play(self, iteration):
        """
        Run parallel self-play using multiple worker processes.
        
        Args:
            iteration: Current training iteration
            
        Returns:
            List of training examples
        """
        num_workers = self.args['num_workers']
        eps_per_worker = self.args['num_eps'] // num_workers
        
        # Shared queues
        request_queue = Queue()
        result_queue = Queue()
        
        # Create response queues for each worker
        response_queues = {}
        for i in range(num_workers):
            response_queues[i] = Queue()
        
        # Start prediction server
        game = self.game_class()
        pred_server = PredictionServer(self.model, game, batch_size=32, timeout=0.05)
        for i in range(num_workers):
            pred_server.response_queues[i] = response_queues[i]
        pred_server.request_queue = request_queue
        pred_server.start()
        
        # Start workers
        processes = []
        for i in range(num_workers):
            p = Process(
                target=run_worker,
                args=(i, self.game_class, self.args, request_queue, response_queues[i], result_queue, eps_per_worker, iteration)
            )
            p.start()
            processes.append(p)
        
        # Collect results
        all_examples = []
        for _ in tqdm(range(num_workers), desc="Collecting"):
            worker_id, examples = result_queue.get()
            all_examples.extend(examples)
        
        # Cleanup
        for p in processes:
            p.join(timeout=5.0)
        pred_server.stop()
        
        return all_examples

    def train_network(self, examples):
        """
        Train neural network on collected examples.
        
        Args:
            examples: List of (board, policy, value) tuples
        """
        optimizer = optim.Adam(self.model.parameters(), lr=self.args['lr'])
        dataset = XiangqiDataset(examples)
        dataloader = DataLoader(dataset, batch_size=self.args['batch_size'], shuffle=True)
        
        self.model.train()
        for epoch in range(self.args['epochs']):
            print(f'EPOCH {epoch + 1}:')
            pi_losses, v_losses = [], []
            
            for boards, pis, vs in tqdm(dataloader, desc="Training"):
                if self.args['cuda']:
                    boards, pis, vs = boards.cuda(), pis.cuda(), vs.cuda()
                
                out_pi, out_v = self.model(boards)
                l_pi = -torch.sum(pis * out_pi) / pis.size()[0]
                l_v = torch.sum((vs - out_v.view(-1)) ** 2) / vs.size()[0]
                total_loss = l_pi + l_v
                
                optimizer.zero_grad()
                total_loss.backward()
                optimizer.step()
                
                pi_losses.append(l_pi.item())
                v_losses.append(l_v.item())
            
            print(f'Loss PI: {np.mean(pi_losses):.4f}, Loss V: {np.mean(v_losses):.4f}')

    def save_checkpoint(self, folder, filename, iteration):
        """Save model checkpoint."""
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            os.makedirs(folder)
        torch.save({
            'state_dict': self.model.state_dict(),
            'iteration': iteration
        }, filepath)

    def _broadcast_status(self, iteration, status):
        """Broadcast training status to server."""
        try:
            requests.post("http://localhost:8000/internal/training/state", json={
                "iteration": iteration,
                "status": status
            }, timeout=0.5)
        except:
            pass

    def learn(self):
        """Main training loop."""
        for i in range(self.start_iteration, self.args['num_iters'] + 1):
            print(f'\n=== Iteration {i} ===')
            
            # Parallel Self-Play
            print("Self-Play (Parallel)...")
            self._broadcast_status(i, "self-play-parallel")
            
            examples = self.parallel_self_play(i)
            self.train_examples_history.append(examples)
            
            # Flatten and shuffle
            all_examples = []
            for e in self.train_examples_history:
                all_examples.extend(e)
            random.shuffle(all_examples)
            
            # Train
            print("Training DNN...")
            self._broadcast_status(i, "training_dnn")
            self.train_network(all_examples)
            
            # Save checkpoint
            self.save_checkpoint(
                self.args['checkpoint'],
                f'checkpoint_{i}.pth.tar',
                i
            )
            print(f"Checkpoint saved: checkpoint_{i}.pth.tar")
