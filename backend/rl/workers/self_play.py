"""
Self-Play Worker for Parallel Training.

Runs MCTS-based self-play in a separate process, communicating with
a central prediction server for batched GPU inference.

Optimized: Uses full MCTS tree search (not simplified single-pass).
"""
import numpy as np
import math
import uuid
import time
from multiprocessing import Process, Queue


class RemoteMCTS:
    """
    MCTS with remote network prediction.
    
    Same algorithm as algorithms/mcts.py, but uses a remote prediction
    function instead of a local model for GPU inference.
    """
    
    def __init__(self, game, predict_fn, args):
        """
        Initialize RemoteMCTS.
        
        Args:
            game: Game instance
            predict_fn: Function (board_tensor) -> (policy, value)
            args: Dict with 'num_mcts_sims' and 'cpuct'
        """
        self.game = game
        self.predict_fn = predict_fn
        self.args = args
        
        self.Qsa = {}  # Q values for (s, a)
        self.Nsa = {}  # Visit counts for (s, a)
        self.Ns = {}   # Visit counts for state s
        self.Ps = {}   # Policy from neural network for state s
        self.Es = {}   # Game ended status for state s
        self.Vs = {}   # Valid moves for state s
    
    def get_action_prob(self, canonical_board, temp=1):
        """Get action probabilities after MCTS search."""
        num_sims = self.args.get('num_mcts_sims', 25)
        
        for _ in range(num_sims):
            self.search(canonical_board)
        
        s = self.game.string_representation(canonical_board)
        counts = [self.Nsa.get((s, a), 0) for a in range(8100)]
        
        if temp == 0:
            bestAs = np.array(np.argwhere(counts == np.max(counts))).flatten()
            bestA = np.random.choice(bestAs)
            probs = [0] * len(counts)
            probs[bestA] = 1
            return probs
        
        counts = [x ** (1.0 / temp) for x in counts]
        counts_sum = float(sum(counts))
        if counts_sum > 0:
            probs = [x / counts_sum for x in counts]
        else:
            probs = [0] * len(counts)
        return probs
    
    def search(self, canonical_board, depth=0):
        """Perform one MCTS iteration with remote prediction."""
        if depth > 100:
            return 0
        
        s = self.game.string_representation(canonical_board)
        
        # Check terminal state
        if s not in self.Es:
            self.Es[s] = self.game.get_game_ended(canonical_board, 1)
        if self.Es[s] != 0:
            return -self.Es[s]
        
        # Leaf node - expand with remote prediction
        if s not in self.Ps:
            board_tensor = self.game.state_to_tensor(canonical_board)
            policy, v = self.predict_fn(board_tensor)
            valids = self.game.get_valid_moves(canonical_board, 1)
            
            # Mask invalid moves
            policy = policy * valids
            sum_policy = np.sum(policy)
            if sum_policy > 0:
                policy /= sum_policy
            else:
                policy = valids / np.sum(valids) if np.sum(valids) > 0 else valids
            
            self.Ps[s] = policy
            self.Ns[s] = 0
            return -v
        
        # Select action with highest UCB
        valids = self.game.get_valid_moves(canonical_board, 1)
        cur_best = -float('inf')
        best_act = -1
        
        cpuct = self.args.get('cpuct', 1.0)
        s_visits = self.Ns[s]
        sqrt_s_visits = math.sqrt(s_visits + 1e-8)
        
        valid_indices = np.where(valids == 1)[0]
        
        for a in valid_indices:
            if (s, a) in self.Qsa:
                u = self.Qsa[(s, a)] + cpuct * self.Ps[s][a] * sqrt_s_visits / (1 + self.Nsa[(s, a)])
            else:
                u = cpuct * self.Ps[s][a] * sqrt_s_visits + 1e-8
            
            if u > cur_best:
                cur_best = u
                best_act = a
        
        if best_act == -1:
            return 0
        
        a = best_act
        
        # Recurse to next state
        next_s, next_player = self.game.get_next_state(canonical_board, 1, a)
        next_s = self.game.get_canonical_form(next_s, next_player)
        
        v = self.search(next_s, depth + 1)
        
        # Backpropagate
        if (s, a) in self.Qsa:
            self.Qsa[(s, a)] = (self.Nsa[(s, a)] * self.Qsa[(s, a)] + v) / (self.Nsa[(s, a)] + 1)
            self.Nsa[(s, a)] += 1
        else:
            self.Qsa[(s, a)] = v
            self.Nsa[(s, a)] = 1
        
        self.Ns[s] += 1
        return -v


class SelfPlayWorker:
    """A worker that runs self-play episodes using remote prediction + full MCTS."""
    
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
        """Run a single self-play episode with full MCTS."""
        trainExamples = []
        board = self.game._init_board()
        current_player = 1
        step = 0
        max_steps = 200  # Match coach.py setting
        
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
            temp = int(step < self.args.get('tempThreshold', 15))
            
            # Create fresh MCTS for this move (like Coach does)
            mcts = RemoteMCTS(self.game, self.predict, self.args)
            pi = mcts.get_action_prob(canonical_board, temp=temp)
            
            # Store example
            state_tensor = self.game.state_to_tensor(canonical_board)
            trainExamples.append([state_tensor, pi, current_player])
            
            # Select action
            action = np.random.choice(len(pi), p=pi)
            
            # Log move - convert from Canonical to Absolute coordinates
            move_coords = self.game.decode_move(action)
            start, end = move_coords
            if current_player == -1:
                start = (start[0], 9 - start[1])
                end = (end[0], 9 - end[1])
            game_record["moves"].append([list(start), list(end)])
            
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


def run_worker(worker_id, game_class, args, request_queue, response_queue, result_queue, num_episodes, iteration):
    """Entry point for worker process."""
    from game import XiangqiGame
    
    game = XiangqiGame()
    worker = SelfPlayWorker(worker_id, game, args, request_queue, response_queue, result_queue)
    
    all_examples = []
    for _ in range(num_episodes):
        examples, game_record = worker.execute_episode(iteration)
        all_examples.extend(examples)
        
    result_queue.put((worker_id, all_examples))

