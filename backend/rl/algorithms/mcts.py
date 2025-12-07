"""
Monte Carlo Tree Search (MCTS) Algorithm.

Implements MCTS with Upper Confidence Bound (UCB) for action selection,
integrated with neural network for policy and value estimation.
"""
import numpy as np
import math


class MCTS:
    """
    Monte Carlo Tree Search with Neural Network guidance.
    
    Uses UCB formula for exploration-exploitation balance:
    UCB = Q(s,a) + c_puct * P(s,a) * sqrt(N(s)) / (1 + N(s,a))
    """
    
    def __init__(self, game, model, args):
        """
        Initialize MCTS.
        
        Args:
            game: Game instance with board operations
            model: Neural network for policy/value prediction
            args: Dict with 'num_mcts_sims' and 'cpuct' keys
        """
        self.game = game
        self.model = model
        self.args = args  # {num_mcts_sims: 50, cpuct: 1.0}
        
        self.Qsa = {}  # Q values for (s, a)
        self.Nsa = {}  # Visit counts for (s, a)
        self.Ns = {}   # Visit counts for state s
        self.Ps = {}   # Policy from neural network for state s
        
        self.Es = {}   # Game ended status for state s
        self.Vs = {}   # Valid moves for state s

    def get_action_prob(self, canonical_board, temp=1):
        """
        Get action probabilities for the given board state.
        
        Args:
            canonical_board: Board from current player's perspective
            temp: Temperature for exploration (0 = greedy, 1 = proportional)
            
        Returns:
            List of probabilities for each action
        """
        for i in range(self.args['num_mcts_sims']):
            self.search(canonical_board)
            
        s = self.game.string_representation(canonical_board)
        counts = [self.Nsa.get((s, a), 0) for a in range(8100)]  # 8100 max actions
        
        if temp == 0:
            bestAs = np.array(np.argwhere(counts == np.max(counts))).flatten()
            bestA = np.random.choice(bestAs)
            probs = [0] * len(counts)
            probs[bestA] = 1
            return probs
        
        counts = [x ** (1.0 / temp) for x in counts]
        counts_sum = float(sum(counts))
        probs = [x / counts_sum for x in counts]
        return probs

    def search(self, canonical_board, depth=0):
        """
        Perform one iteration of MCTS.
        
        Args:
            canonical_board: Board from current player's perspective
            depth: Current search depth (for recursion limit)
            
        Returns:
            Negative of the value (for minimax-style backprop)
        """
        if depth > 500:
            return 0  # Depth limit to prevent infinite recursion

        s = self.game.string_representation(canonical_board)
        
        # Check terminal state
        if s not in self.Es:
            self.Es[s] = self.game.get_game_ended(canonical_board, 1)
        if self.Es[s] != 0:
            return -self.Es[s]

        # Leaf node - expand and evaluate
        if s not in self.Ps:
            board_tensor = self.game.state_to_tensor(canonical_board)
            policy, v = self.model.predict(board_tensor)
            valids = self.game.get_valid_moves(canonical_board, 1)
            
            # Mask invalid moves
            policy = policy * valids
            sum_policy = np.sum(policy)
            if sum_policy > 0:
                policy /= sum_policy
            else:
                # All valid moves were masked (rare case)
                # Fallback to uniform random among valid moves
                policy = policy + valids
                policy /= np.sum(policy)
                
            self.Ps[s] = policy
            self.Ns[s] = 0
            return -v

        # Select action with highest UCB
        valids = self.game.get_valid_moves(canonical_board, 1)
        cur_best = -float('inf')
        best_act = -1
        
        s_visits = self.Ns[s]
        sqrt_s_visits = math.sqrt(s_visits + 1e-8)
        
        # Only iterate over valid moves for efficiency
        valid_indices = np.where(valids == 1)[0]
        
        for a in valid_indices:
            if (s, a) in self.Qsa:
                u = self.Qsa[(s, a)] + self.args['cpuct'] * self.Ps[s][a] * sqrt_s_visits / (1 + self.Nsa[(s, a)])
            else:
                u = self.args['cpuct'] * self.Ps[s][a] * sqrt_s_visits + 1e-8
            
            if u > cur_best:
                cur_best = u
                best_act = a
        
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
