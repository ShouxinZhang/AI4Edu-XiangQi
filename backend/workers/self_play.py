"""
Self-Play Worker for Parallel Training.
Runs MCTS-based self-play in a separate process.
"""
import numpy as np
import uuid
import time
from multiprocessing import Process, Queue
import sys
sys.path.insert(0, '..')  # Ensure parent directory is in path

class SelfPlayWorker:
    """
    A worker that runs self-play episodes using a remote prediction service.
    """
    def __init__(self, worker_id, game, args, request_queue, response_queue, result_queue):
        self.worker_id = worker_id
        self.game = game
        self.args = args
        self.request_queue = request_queue
        self.response_queue = response_queue
        self.result_queue = result_queue
        
    def predict(self, board_tensor):
        """Request prediction from the server."""
        self.request_queue.put((self.worker_id, board_tensor))
        return self.response_queue.get()
        
    def execute_episode(self, iteration=0):
        """
        Run a single self-play episode.
        Returns list of (state, policy, reward) tuples.
        """
        trainExamples = []
        board = self.game._init_board()
        current_player = 1
        step = 0
        max_steps = 100
        
        game_record = {
            "game_id": str(uuid.uuid4()),
            "iteration": iteration,
            "timestamp": time.time(),
            "moves": [],
            "winner": 0
        }
        
        while step < max_steps:
            step += 1
            canonical_board = self.game.get_canonical_form(board, current_player)
            temp = int(step < self.args['tempThreshold'])
            
            # Get action probabilities using simplified MCTS with remote prediction
            pi = self._get_action_prob(canonical_board, temp)
            
            # Store example
            state_tensor = self.game.state_to_tensor(canonical_board)
            trainExamples.append([state_tensor, pi, current_player])
            
            # Select action
            action = np.random.choice(len(pi), p=pi)
            
            # Log move
            move_coords = self.game.decode_move(action)
            game_record["moves"].append(list(move_coords))
            
            # Execute move
            board, current_player = self.game.get_next_state(board, current_player, action)
            
            # Check game end
            r = self.game.get_game_ended(board, current_player)
            if r != 0:
                game_record["winner"] = r
                return [(x[0], x[1], r * ((-1) ** (x[2] != current_player))) for x in trainExamples], game_record
        
        # Max steps reached - draw
        game_record["winner"] = 0
        return [(x[0], x[1], 0) for x in trainExamples], game_record
    
    def _get_action_prob(self, canonical_board, temp):
        """
        Simplified MCTS with remote prediction.
        For full parallel MCTS, this would need more complex tree management.
        """
        # For now, use direct policy from network (simplified)
        # Full implementation would run MCTS simulations
        state_tensor = self.game.state_to_tensor(canonical_board)
        policy, value = self.predict(state_tensor)
        
        # Mask invalid moves
        valids = self.game.get_valid_moves(canonical_board, 1)
        policy = policy * valids
        
        policy_sum = np.sum(policy)
        if policy_sum > 0:
            policy = policy / policy_sum
        else:
            # Fallback to uniform random among valid moves
            policy = valids / np.sum(valids)
            
        if temp == 0:
            # Greedy selection
            best_action = np.argmax(policy)
            probs = np.zeros(len(policy))
            probs[best_action] = 1.0
            return probs
            
        return policy


def run_worker(worker_id, game_class, args, request_queue, response_queue, result_queue, num_episodes, iteration):
    """
    Entry point for worker process.
    """
    from game import XiangqiGame
    
    game = XiangqiGame()
    worker = SelfPlayWorker(worker_id, game, args, request_queue, response_queue, result_queue)
    
    all_examples = []
    for _ in range(num_episodes):
        examples, game_record = worker.execute_episode(iteration)
        all_examples.extend(examples)
        
    result_queue.put((worker_id, all_examples))
