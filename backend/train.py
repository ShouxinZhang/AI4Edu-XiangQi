import os
import numpy as np
import random
import time
import torch
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
import requests
import json
import datetime
import uuid
import sys

sys.setrecursionlimit(10000)

from game import XiangqiGame, BOARD_HEIGHT, BOARD_WIDTH
from model import XiangqiNet
from mcts import MCTS

class GameLogger:
    def __init__(self, log_dir="data/evolution"):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def log_game(self, iteration, game_record):
        filename = os.path.join(self.log_dir, f"iter_{iteration}_games.jsonl")
        with open(filename, "a") as f:
            f.write(json.dumps(game_record) + "\n")

class BroadcastClient:
    def __init__(self, url="http://localhost:8000/internal/training/update"):
        self.url = url

    def broadcast(self, data):
        try:
            requests.post(self.url, json=data, timeout=0.1)
        except:
            pass # Ignore errors to not stop training

class XiangqiDataset(Dataset):
    def __init__(self, examples):
        self.examples = examples

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        board, pi, v = self.examples[idx]
        return torch.FloatTensor(board), torch.FloatTensor(pi), torch.FloatTensor([v])

class Coach:
    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.args = args
        self.mcts = MCTS(game, nnet, args)
        self.trainExamplesHistory = []
        
        # Visualization & Logging
        self.logger = GameLogger()
        self.broadcaster = BroadcastClient()

    def executeEpisode(self, iteration=0):
        trainExamples = []
        board = self.game._init_board() # Initialize raw board
        self.curPlayer = 1
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
            canonicalBoard = self.game.get_canonical_form(board, self.curPlayer)
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
            except: pass
            
            # Use MCTS to get action probabilities
            # Reset MCTS for current state search?
            # AlphaZero usually retains MCTS tree but here we simple-implementation:
            # Recreate MCTS or just prune? 
            # My simple MCTS implementation is stateless regarding tree root moves (dictionary based).
            # So just calling search works, but we should clear tree if memory issues or just keep building.
            # In deep learning, usually we assume fresh MCTS or reused tree.
            # My usage: self.mcts = MCTS(...) in init.
            # If I don't reset, the tree grows indefinitely.
            # For simplicity: Reset MCTS each move or let it grow if memory allows?
            # Let's reset for now to be safe on memory.
            self.mcts = MCTS(self.game, self.nnet, self.args)
            
            pi = self.mcts.get_action_prob(canonicalBoard, temp=temp)
            
            # Store example: (canonicalBoard, pi, v?)
            # v is unknown until game ends.
            sym = self.game.get_canonical_form(board, self.curPlayer)
            trainExamples.append([self.game.to_tensor().copy(), pi, self.curPlayer]) 
            # Note: stored game.to_tensor() which uses current board state logic.
            # Wait, game.to_tensor() uses self.game.board.
            # I must ensure self.game.board syncs with local 'board' variable if I use it.
            # Actually, executeEpisode should probably use self.game to maintain state
            # but I am using 'board' variable.
            # Let's sync: self.game.board = board
            self.game.board = board
            self.game.current_player = self.curPlayer
            
            trainExamples[-1][0] = self.game.to_tensor() # store tensor state

            action = np.random.choice(len(pi), p=pi)
            
            # Log move
            move_coords = self.game.decode_move(action)
            game_record["moves"].append(list(move_coords)) # Store as [[x1,y1], [x2,y2]]
            
            board, self.curPlayer = self.game.get_next_state(board, self.curPlayer, action)

            r = self.game.get_game_ended(board, self.curPlayer)
            if r != 0:
                game_record["winner"] = r
                self.logger.log_game(iteration, game_record)
                
                # Broadcast Game Result
                try:
                    # Update server state history
                    requests.post("http://localhost:8000/internal/training/state", json={
                        "history_update": {
                            "id": game_record["game_id"][:8],
                            "winner": r,
                            "steps": episodeStep,
                            "timestamp": int(time.time()),
                            "episode": iteration  # Using iteration as "Generation"
                        }
                    }, timeout=0.1)
                except: pass
                
                return [(x[0], x[1], r * ((-1) ** (x[2] != self.curPlayer))) for x in trainExamples]

            # MAX STEPS CHECK
            if episodeStep >= 100:
                r = 0 # Draw
                game_record["winner"] = r
                self.logger.log_game(iteration, game_record)

                try:
                    requests.post("http://localhost:8000/internal/training/state", json={
                        "history_update": {
                            "id": game_record["game_id"][:8],
                            "winner": r,
                            "steps": episodeStep,
                            "timestamp": int(time.time()),
                            "episode": iteration
                        }
                    }, timeout=0.1)
                except: pass
                
                # Return examples with 0 reward
                return [(x[0], x[1], 0) for x in trainExamples]

    def learn(self):
        for i in range(1, self.args['num_iters'] + 1):
            print(f'Starting Iteration {i} ...')
            iterationTrainExamples = []
            
            # Update training state
            try:
                requests.post("http://localhost:8000/internal/training/state", json={
                    "iteration": i,
                    "total_episodes": self.args['num_eps'],
                    "episode": 0,
                    "status": "self-play"
                }, timeout=0.5)
            except: pass
            
            for ep in tqdm(range(self.args['num_eps']), desc="Self Play"):
                # Update episode progress
                try:
                    requests.post("http://localhost:8000/internal/training/state", json={
                        "episode": ep + 1
                    }, timeout=0.1)
                except: pass
                
                iterationTrainExamples += self.executeEpisode(iteration=i)
            
            # Save the iteration examples to history 
            self.trainExamplesHistory.append(iterationTrainExamples)
            
            # Flatten history
            trainExamples = []
            for e in self.trainExamplesHistory:
                trainExamples.extend(e)
            random.shuffle(trainExamples)
            
            # Train
            try:
                requests.post("http://localhost:8000/internal/training/state", json={
                    "status": "training_dnn"
                }, timeout=0.1)
            except: pass
            
            self.train(trainExamples)
            
            # Save checkpoint
            self.save_checkpoint(folder='checkpoints', filename=f'checkpoint_{i}.pth.tar')

    def train(self, examples):
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

                # compute output
                out_pi, out_v = self.nnet(boards)
                
                l_pi = self.loss_pi(out_pi, pis)
                l_v = self.loss_v(out_v, vs)
                total_loss = l_pi + l_v
                
                optimizer.zero_grad()
                total_loss.backward()
                optimizer.step()
                
                pi_losses.append(l_pi.item())
                v_losses.append(l_v.item())
            
            print(f'Loss PI: {np.mean(pi_losses)}, Loss V: {np.mean(v_losses)}')

    def loss_pi(self, targets, outputs):
        return -torch.sum(targets * outputs) / targets.size()[0]

    def loss_v(self, targets, outputs):
        return torch.sum((targets - outputs.view(-1)) ** 2) / targets.size()[0]

    def save_checkpoint(self, folder='checkpoints', filename='checkpoint.pth.tar'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            os.makedirs(folder)
        torch.save({
            'state_dict': self.nnet.state_dict(),
        }, filepath)

if __name__ == "__main__":
    game = XiangqiGame()
    nnet = XiangqiNet()
    
    args = {
        'num_iters': 1000,
        'num_eps': 10, # Number of complete self-play games to simulate per iteration
        'tempThreshold': 15,
        'updateThreshold': 0.6,
        'maxlenOfQueue': 200000,
        'num_mcts_sims': 25, # Number of MCTS simulations per move
        'cpuct': 1.0,
        'checkpoint': './checkpoints',
        'load_model': False,
        'load_folder_file': ('/dev/models/8x8/tictactoe', 'best.pth.tar'),
        'lr': 0.001,
        'dropout': 0.3,
        'epochs': 10,
        'batch_size': 512, # Increased from 64 for VRAM usage
        'cuda': torch.cuda.is_available(),
        'num_channels': 512,
    }
    
    if args['cuda']:
        nnet.cuda()
    
    coach = Coach(game, nnet, args)
    coach.learn()
