"""
Coach - AlphaZero Training Loop.

Manages self-play, training, and evaluation cycles.
"""
import os
import numpy as np
import random
import time
import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm
import requests
import uuid

from ..algorithms.mcts import MCTS
from .dataset import XiangqiDataset
from .logger import GameLogger
from .broadcast import BroadcastClient


class Coach:
    """
    AlphaZero-style training coach.
    
    Manages the training loop: self-play -> collect examples -> train network.
    """
    
    def __init__(self, game, nnet, args):
        """
        Initialize coach.
        
        Args:
            game: Game instance
            nnet: Neural network model
            args: Training configuration dict
        """
        self.game = game
        self.nnet = nnet
        self.args = args
        self.mcts = MCTS(game, nnet, args)
        self.trainExamplesHistory = []
        
        # Visualization & Logging
        self.logger = GameLogger()
        self.broadcaster = BroadcastClient()
        
        # Starting iteration (for resume)
        self.start_iteration = 1

    def execute_episode(self, iteration=0):
        """
        Execute one episode of self-play.
        
        Args:
            iteration: Current training iteration number
            
        Returns:
            List of (board_tensor, policy, value) training examples
        """
        trainExamples = []
        board = self.game._init_board()
        curPlayer = 1
        episodeStep = 0
        
        # Game Record for Logging
        game_record = {
            "game_id": str(uuid.uuid4()),
            "iteration": iteration,
            "timestamp": time.time(),
            "moves": [],
            "winner": 0
        }
        
        while True:
            episodeStep += 1
            canonicalBoard = self.game.get_canonical_form(board, curPlayer)
            temp = int(episodeStep < self.args['tempThreshold'])
            
            # Broadcast current state
            try:
                self.broadcaster.broadcast({
                    "type": "step",
                    "data": {
                        "board": board.tolist(),
                        "step": episodeStep
                    }
                })
            except:
                pass
            
            # Reset MCTS each move to save memory
            self.mcts = MCTS(self.game, self.nnet, self.args)
            pi = self.mcts.get_action_prob(canonicalBoard, temp=temp)
            
            # Store example
            self.game.board = board
            self.game.current_player = curPlayer
            trainExamples.append([self.game.to_tensor().copy(), pi, curPlayer])

            action = np.random.choice(len(pi), p=pi)
            
            # Log move - convert from Canonical to Absolute coordinates
            move_coords = self.game.decode_move(action)
            start, end = move_coords
            
            # When curPlayer is Black (-1), canonical board was flipped
            # So we need to flip y-coordinates back: y -> 9 - y
            if curPlayer == -1:
                start = (start[0], 9 - start[1])
                end = (end[0], 9 - end[1])
            
            game_record["moves"].append([list(start), list(end)])
            
            board, curPlayer = self.game.get_next_state(board, curPlayer, action)

            r = self.game.get_game_ended(board, curPlayer)
            if r != 0:
                game_record["winner"] = r
                self.logger.log_game(iteration, game_record)
                self._broadcast_game_result(game_record, episodeStep, iteration)
                return [(x[0], x[1], r * ((-1) ** (x[2] != curPlayer))) for x in trainExamples]

            # MAX STEPS CHECK
            max_steps = self.args.get('max_steps', 200)
            if episodeStep >= max_steps:
                game_record["winner"] = 0
                self.logger.log_game(iteration, game_record)
                self._broadcast_game_result(game_record, episodeStep, iteration)
                return [(x[0], x[1], 0) for x in trainExamples]

    def _broadcast_game_result(self, game_record, steps, iteration):
        """Broadcast game result to server."""
        try:
            requests.post("http://localhost:8000/internal/training/state", json={
                "history_update": {
                    "id": game_record["game_id"][:8],
                    "winner": game_record["winner"],
                    "steps": steps,
                    "timestamp": int(time.time()),
                    "episode": iteration
                }
            }, timeout=0.1)
        except:
            pass

    def learn(self):
        """Main training loop."""
        for i in range(self.start_iteration, self.args['num_iters'] + 1):
            print(f'Starting Iteration {i} ...')
            iterationTrainExamples = []
            
            # Update training state
            self._broadcast_status(i, 0, "self-play")
            
            for ep in tqdm(range(self.args['num_eps']), desc="Self Play"):
                self._broadcast_episode(ep + 1)
                iterationTrainExamples += self.execute_episode(iteration=i)
            
            # Save to history
            self.trainExamplesHistory.append(iterationTrainExamples)
            
            # Flatten and shuffle
            trainExamples = []
            for e in self.trainExamplesHistory:
                trainExamples.extend(e)
            random.shuffle(trainExamples)
            
            # Train
            self._broadcast_status(i, self.args['num_eps'], "training_dnn")
            self.train(trainExamples)
            
            # Save checkpoint
            self.save_checkpoint(folder='checkpoints', filename=f'checkpoint_{i}.pth.tar', iteration=i)
            
            # Evaluate every 10 iterations
            if i % 10 == 0:
                self.evaluate(i)

    def _broadcast_status(self, iteration, episode, status):
        """Broadcast training status."""
        try:
            requests.post("http://localhost:8000/internal/training/state", json={
                "iteration": iteration,
                "total_episodes": self.args['num_eps'],
                "episode": episode,
                "status": status
            }, timeout=0.5)
        except:
            pass

    def _broadcast_episode(self, episode):
        """Broadcast episode progress."""
        try:
            requests.post("http://localhost:8000/internal/training/state", json={
                "episode": episode
            }, timeout=0.1)
        except:
            pass

    def train(self, examples):
        """Train the neural network on collected examples."""
        optimizer = optim.Adam(self.nnet.parameters(), lr=self.args['lr'])
        dataset = XiangqiDataset(examples)
        dataloader = DataLoader(dataset, batch_size=self.args['batch_size'], shuffle=True)
        
        self.nnet.train()
        for epoch in range(self.args['epochs']):
            print(f'EPOCH {epoch + 1}:')
            pi_losses = []
            v_losses = []
            
            for boards, pis, vs in tqdm(dataloader, desc="Training"):
                if self.args['cuda']:
                    boards, pis, vs = boards.cuda(), pis.cuda(), vs.cuda()

                out_pi, out_v = self.nnet(boards)
                
                l_pi = self._loss_pi(out_pi, pis)
                l_v = self._loss_v(out_v, vs)
                total_loss = l_pi + l_v
                
                optimizer.zero_grad()
                total_loss.backward()
                optimizer.step()
                
                pi_losses.append(l_pi.item())
                v_losses.append(l_v.item())
            
            print(f'Loss PI: {np.mean(pi_losses):.4f}, Loss V: {np.mean(v_losses):.4f}')

    def _loss_pi(self, outputs, targets):
        """Policy loss (cross-entropy)."""
        return -torch.sum(targets * outputs) / targets.size()[0]

    def _loss_v(self, outputs, targets):
        """Value loss (MSE)."""
        return torch.sum((targets - outputs.view(-1)) ** 2) / targets.size()[0]

    def evaluate(self, iteration):
        """Evaluate model against MinimaxPlayer."""
        from ..evaluation.arena import Arena
        from ..evaluation.players import AlphaZeroPlayer, MinimaxPlayer
        
        print(f"\n=== Evaluation at Iteration {iteration} ===")
        
        az_player = AlphaZeroPlayer(self.game, self.nnet, self.args, temp=0)
        minimax_player = MinimaxPlayer(self.game, depth=2)
        
        arena = Arena(az_player, minimax_player, self.game)
        az_wins, mm_wins, draws = arena.play_games(10, verbose=False)
        
        print(f"AlphaZero vs Minimax: {az_wins} wins, {mm_wins} losses, {draws} draws")
        win_rate = az_wins / 10.0
        print(f"Win Rate: {win_rate * 100:.1f}%")
        
        # Broadcast evaluation result
        try:
            requests.post("http://localhost:8000/internal/training/state", json={
                "eval_result": {
                    "iteration": iteration,
                    "az_wins": az_wins,
                    "mm_wins": mm_wins,
                    "draws": draws,
                    "win_rate": win_rate
                }
            }, timeout=0.5)
        except:
            pass

    def save_checkpoint(self, folder='checkpoints', filename='checkpoint.pth.tar', iteration=0):
        """Save model checkpoint."""
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            os.makedirs(folder)
        torch.save({
            'state_dict': self.nnet.state_dict(),
            'iteration': iteration
        }, filepath)
