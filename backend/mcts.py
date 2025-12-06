
import numpy as np
import math
import copy

class MCTS:
    def __init__(self, game, model, args):
        self.game = game
        self.model = model
        self.args = args # {num_mcts_sims: 50, cpuct: 1.0}
        
        self.Qsa = {} # stores Q values for s,a (as (s,a))
        self.Nsa = {} # stores #times edge s,a was visited
        self.Ns = {} # stores #times board s was visited
        self.Ps = {} # stores initial policy (returned by neural net)
        
        self.Es = {} # stores game.getGameEnded ended for board s
        self.Vs = {} # stores game.getValidMoves for board s

    def get_action_prob(self, canonical_board, temp=1):
        for i in range(self.args['num_mcts_sims']):
            self.search(canonical_board)
            
        s = self.game.string_representation(canonical_board)
        counts = [self.Nsa.get((s, a), 0) for a in range(8100)] # 8100 max actions
        
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
        if depth > 500: return 0 # Depth limit to prevent infinite recursion

        s = self.game.string_representation(canonical_board)
        
        if s not in self.Es:
            self.Es[s] = self.game.get_game_ended(canonical_board, 1)
        if self.Es[s] != 0:
            # terminal node
            return -self.Es[s]

        if s not in self.Ps:
            # leaf node
            # 1. Expand
            # 2. Evaluate
            board_tensor = self.game.state_to_tensor(canonical_board)
            policy, v = self.model.predict(board_tensor)
            valids = self.game.get_valid_moves(canonical_board, 1)
            
            # Mask invalid moves
            policy = policy * valids
            sum_policy = np.sum(policy)
            if sum_policy > 0:
                policy /= sum_policy
            else:
                # All valid moves were masked? (Should be rare)
                # Uniform random valid moves
                policy = policy + valids
                policy /= np.sum(policy)
                
            self.Ps[s] = policy
            self.Ns[s] = 0
            return -v

        # Select
        valids = self.game.get_valid_moves(canonical_board, 1)
        cur_best = -float('inf')
        best_act = -1
        
        # Upper Confidence Bound
        s_visits = self.Ns[s]
        sqrt_s_visits = math.sqrt(s_visits + 1e-8)
        
        # Pick action with highest UCB
        # We only iterate valid moves
        # But looping 8100 is slow. Optimization: iterate indices where valids[a] > 0
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
        # Recurse
        next_s, next_player = self.game.get_next_state(canonical_board, 1, a)
        # Note: get_next_state returns board from perspective of next_player (-1)
        # So we pass it to search, which expects canonical board
        next_s = self.game.get_canonical_form(next_s, next_player)

        v = self.search(next_s, depth + 1)
        
        # Backprop
        if (s, a) in self.Qsa:
            self.Qsa[(s, a)] = (self.Nsa[(s, a)] * self.Qsa[(s, a)] + v) / (self.Nsa[(s, a)] + 1)
            self.Nsa[(s, a)] += 1
        else:
            self.Qsa[(s, a)] = v
            self.Nsa[(s, a)] = 1
            
        self.Ns[s] += 1
        return -v
