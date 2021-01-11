import math
import os
import pickle
import random
from time import time
from collections import defaultdict

import agent
import board
import heuristic


class MCTS(agent.Agent):
    ''' Chess agent using either canonical or modified Monte Carlo Tree 
    Search, in particular including the option to stop rollouts early and 
    evaluate them heuristically, select already-seen paths heuristically, or
    conduct simulation rollouts heuristically. Automatically reuses tree 
    within sessions, and can save between sessions. Note that depth only 
    refers to simulation depth, not rollout depth.'''
    def __init__(self, side, max_depth, n_rollouts, variant, heuristic_simulation, heuristic_selection, input_path, output_path, ucb_const):
        self.side = side
        self.max_depth = max_depth
        self.n_rollouts = n_rollouts
        self.variant = variant
        self.heuristic_simulation = heuristic_simulation
        self.heuristic_selection = heuristic_selection
        self.ucb_const = ucb_const
        self.input_path = input_path
        self.output_path = output_path
        if input_path:
            self.load_root()
        else:
            self.root = Node(board.set_board(variant), None, self.ucb_const)
        self.cur = self.root

    def load_root(self):
        ''' Loads saved root from pickle file specified in input_path.'''
        file = open(os.path.join('saves', self.input_path), 'rb')
        self.root = pickle.load(file)
    
    def store_root(self):
        ''' Stores root in pickle file specified in output_path.'''
        if self.output_path:
            file = open(os.path.join('saves', self.output_path), 'wb')
            pickle.dump(self.root, file)

    def reset(self, side):
        ''' Reset current position to root to prepare for a new game.'''
        self.cur = self.root
        self.side = side

    def get_move(self, chessboard, pos_counts):
        ''' Return a move based on tree developed at least in part from 
        rollouts from current position.'''
        result = self.do_rollouts(pos_counts)
        return result

    def record_move(self, move):
        ''' Update current position based on self's or opponent's move.'''
        if move not in self.cur.children.keys():
            self.cur.add_move(move)
        self.cur = self.cur.children[move]
        self.side *= -1

    def do_rollouts(self, pos_counts):
        ''' Conduct MCTS rollouts, of depth and number specified in init, 
        and return the move resulting in highest win percentage or best
        average heuristic evaluation during both these rollouts and any
        previous ones. pos_counts is a position counter used to determine
        threefold repetition.'''
        for i in range(self.n_rollouts):
            side = self.side
            cur = self.cur
            cur.visits += 1
            # Selection phase
            # Using -side here because we're checking whether the *last*
            # move, i.e. by the opposite side, ended the game
            while board.get_result(cur.chessboard, pos_counts, self.variant,\
                                   -side, False) is None:
                if len(cur.children) != len(board.get_all_moves(cur.chessboard, side)):
                     break
                # Note that values() here is dict values (i.e. nodes)
                best_child = list(cur.children.values())[0]
                for child in list(cur.children.values())[1:]:
                    if child.UCB_weight(side, self.heuristic_selection) >\
                       best_child.UCB_weight(side, self.heuristic_selection):
                        best_child = child
                cur = best_child
                side *= -1
                cur.visits += 1
            else:
                # If we found a terminal node, just ignore this rollout
                continue
            # Expansion phase
            # cur is a non-terminal node with incompletely explored children
            moves = board.get_all_moves(cur.chessboard, side)
            random.shuffle(moves)
            # Iterate through possible moves until we find one that isn't
            # already a child of cur
            for move in moves:
                if cur.add_move(move):
                    break
            expanded = cur.children[move]
            expanded.visits += 1
            # Simulation phase
            # -side since side corresponds to cur, not expanded
            pos_counts[cur.chessboard] += 1
            outcome = self.random_to_end(expanded.chessboard, pos_counts, -side, 0)
            pos_counts[cur.chessboard] -= 1
            # Backprop phase
            expanded.update_value(outcome, self.cur, pos_counts)
        
        best_move = list(self.cur.children.keys())[0]
        for move in self.cur.children:
            child = self.cur.children[move]
            best_child = self.cur.children[best_move]
            if self.side*(child.get_value()-best_child.get_value()) > 0:
                best_move = move

        return best_move

    def random_to_end(self, chessboard, pos_counts, side, depth):
        ''' Simulates the rest of the game from a certain state, down to a
        given depth (or until game end if depth=0).''' 
        result = board.get_result(chessboard, pos_counts, self.variant, -side, False)
        if result is not None:
            # Convert to centipawn space (simulated results are in centipawn
            # space thus x100000 here, node values are in win prob. space)
            return result*100000
        elif self.max_depth != 0 and depth == self.max_depth:
            return heuristic.evaluate(chessboard)
        elif self.heuristic_simulation:
            move = heuristic.order_moves_naive(chessboard, side)[0] 
        else:
            moves = board.get_all_moves(chessboard, side)
            random.shuffle(moves)
            move = moves[0]
        new_board = board.make_move(chessboard, *move)
        pos_counts[new_board] += 1
        outcome = self.random_to_end(new_board, pos_counts, -side, depth+1)
        pos_counts[new_board] -= 1
        return outcome


class Node(object):
    ''' Game state node used in MCTS.'''
    
    def __init__(self, chessboard, parent_node, ucb_const):
        self.chessboard = chessboard
        self.parent = parent_node
        self.children = {}
        self.ucb_const = ucb_const
        self.visits = 0
        self.value = float("nan")
        
    def add_move(self, move):
        ''' Adds a new node for the child state resulting from move if one 
        doesn't already exist. Returns true if a new node was added, 
        false otherwise.'''
        if move not in self.children:
            chessboard = board.make_move(self.chessboard, move[0], move[1])
            self.children[move] = Node(chessboard, self, self.ucb_const)
            return True
        return False
    
    def get_value(self):
        ''' Gets the value estimate for the current state, corresponding to 
        the win probability of each side in that state (-1 to 1 for a certain
        Black win to a certain White win).'''
        return self.value

    def update_value(self, outcome, cur, pos_counts):
        ''' Updates the value estimate for this node given a simulated 
        outcome, and averages its new value into its parents' values. 
        Since outcome is in centipawn space, its values are +100000 for a 
        first player win, -100000 for a second player win, 0 for a draw, or 
        some heuristic evaluation in between.'''
        # Reset value (will set it with either outcome or child average)
        self.value = 0
        # If a leaf node, set value to just be outcome as a win prob.
        if len(self.children) == 0:
            # Convert heuristic into winning prob. using logistic model
            if outcome in (100000, -100000, 0):
                self.value = outcome/100000
            else:
                # Based on model described in https://www.chessprogramming.org/Pawn_Advantage,_Win_Percentage,_and_Elo
                self.value = 2/(1+10**(-outcome/4)) - 1
        # If not a leaf node, set new value to be average of children
        for child in self.children.values():
            self.value = (self.value*self.visits + child.value*child.visits)/(self.visits + child.visits)
        # Backprop to parents
        if self.parent and self is not cur:
            self.parent.update_value(0, cur, pos_counts)

    def UCB_weight(self, side, heuristic_selection):
        ''' Weight from the UCB formula used by parent to select a child.
        If heuristic_selection is True, uses heuristic value of current 
        state as a biasing factor in the return value. (Note that this is
        different from the current MCTS value of the node, which is always
        used as an additive component of the UCB weight.)'''
        explore_val = self.ucb_const * math.sqrt(math.log(self.parent.visits)/self.visits)
        if heuristic_selection:
            heuristic_val = 1/(1+10**(-side*heuristic.evaluate(self.chessboard)))
            return self.value*side + heuristic_val*explore_val
        else:
            return self.value*side + explore_val
