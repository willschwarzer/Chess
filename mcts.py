import os
import pickle
import random
from time import time

import agent
import board
import heuristic
class MCTS(agent.Agent):
    def __init__(self, side, max_depth, n_rollouts, variant, use_heuristic, input_path, output_path):
        self.side = side
        self.max_depth = max_depth
        self.n_rollouts = n_rollouts
        self.variant = variant
        self.use_heuristic = use_heuristic
        self.input_path = input_path
        self.output_path = output_path
        if input_path:
            self.load_root()
        else:
            self.root = Node(board.set_board(variant), None)
            
        self.cur = self.root

    def load_root(self):
        file = open(os.path.join('saves', self.input_path), 'rb')
        self.root = pickle.load(file)
    
    def store_root(self):
        if self.output_path:
            file = open(os.path.join('saves', self.output_path), 'wb')
            pickle.dump(self.root, file)

    def reset(self):
        self.cur = self.root

    def get_move(self, chessboard, pos_counts):
        # then = time()
        result = self.do_rollouts(pos_counts)
        # now = time()-then
        # print("get_move took " + str(now) + " seconds")
        return result

    def record_move(self, move):
        if move not in self.cur.children.keys():
            self.cur.add_move(move)
        self.cur = self.cur.children[move]
        self.switch_sides()


    def do_rollouts(self, pos_counts):
        side = self.side
        for i in range(self.n_rollouts):
            cur = self.cur
            cur.visits += 1
            pos_counts[cur.chessboard] += 1
            while len(cur.children) == len(board.get_all_moves(cur.chessboard, self.side))\
             and not (board.get_result(cur.chessboard, pos_counts, self.variant, self.side) is None):
                best_child = list(cur.children.values())[0]
                for child in list(cur.children.values())[1:]:
                    if side*(child.UCB_weight()-bestChild.UCB_weight()) > 0:
                        best_child = child
                cur = best_child
                side *= -1
                cur.visits += 1
                pos_counts[cur.chessboard] += 1
            if board.get_result(cur.chessboard, pos_counts, self.variant, self.side) is not None:
                continue
            for move in board.get_all_moves(cur.chessboard, side):
                if cur.add_move(move):
                    break
            expanded = cur.children[move]
            expanded.visits += 1
            outcome = self.random_to_end(expanded.chessboard, pos_counts, side, 0)
            expanded.update_value(outcome, self.cur, pos_counts)
            pos_counts[cur.chessboard] -= 1
        
        best_move = list(self.cur.children.keys())[0]
        for move in self.cur.children:
            child = self.cur.children[move]
            best_child = self.cur.children[best_move]
            if self.side*(child.get_value()-best_child.get_value()) > 0:
                best_move = move
            
        return best_move

    def random_to_end(self, chessboard, pos_counts, side, depth):
        ''' side: which player's move it is in position chessboard''' 
        result = board.get_result(chessboard, pos_counts, self.variant, -side, False)
        if result is not None:
            # Return a large number since we might be stopping early and doing
            # a heuristic evaluation, which might be bigger than 1 or -1
            return result*100000
        elif self.max_depth != 0 and depth == self.max_depth:
            return heuristic.evaluate(chessboard)
        elif self.use_heuristic:
            move = self.order_moves_naive(chessboard, side)[0] 
        else:
            moves = board.get_all_moves(chessboard, side)
            if not moves:
                breakpoint()
            random.shuffle(moves)
            move = moves[0]
        # if board.piece_at_square(chessboard, *move[0]) == 11:
            # board.print_board(chessboard)
            # print(board.get_castling_rights(chessboard, 1))
            # print()
        new_board = board.make_move(chessboard, *move)
        pos_counts[new_board] += 1
        outcome = self.random_to_end(new_board, pos_counts, -side, depth+1)
        pos_counts[new_board] -= 1
        return outcome

    def order_moves_naive(self, chessboard, side):
        '''Given a board and a side, naively orders the set of all possible moves based solely on whether or not they involve the capture of a piece, and if so, how much the piece is worth.'''
        moves = board.get_all_moves(chessboard, side)
        moves_and_values = [(move, heuristic.evaluate(board.make_move(chessboard, move[0], move[1]))) for move in moves]
        moves_and_values.sort(reverse=(side==1), key=lambda x: x[1])
        return [tup[0] for tup in moves_and_values]


class Node(object):
    """Node used in MCTS"""
    
    def __init__(self, chessboard, parent_node):
        """Constructor for a new node representing game state
        state. parent_node is the Node that is the parent of this
        one in the MCTS tree. """
        self.chessboard = chessboard
        self.parent = parent_node
        self.children = {} # maps moves (keys) to Nodes (values); if you use it differently, you must also change addMove
        self.visits = 0
        self.value = float("nan")
        # Note: you may add additional fields if needed
        
    def add_move(self, move):
        """
        Adds a new node for the child resulting from move if one doesn't already exist.
        Returns true if a new node was added, false otherwise.
        """
        if move not in self.children:
            chessboard = board.make_move(self.chessboard, move[0], move[1])
            self.children[move] = Node(chessboard, self)
            return True
        return False
    
    def get_value(self):
        """
        Gets the value estimate for the current node. Value estimates should correspond
        to the win percentage for the player at this node (accounting for draws as in 
        the project description).
        """
        return self.value

    def update_value(self, outcome, cur, pos_counts):
        """Updates the value estimate for the node's state.
        outcome: +100000 for a first player win, -100000 for a second player win, 0 for a draw, or some heuristic evaluation in between"""
        # NOTE: which outcome is preferred depends on self.state.turn()
        pos_counts[self.chessboard] -= 1
        self.value = 0
        if len(self.children) == 0:
            self.value = outcome
        for child in self.children.values():
            self.value += child.value * child.visits
        if self.parent and self is not cur:
            self.parent.update_value(0, cur, pos_counts)

    def UCB_weight(self, side):
        """Weight from the UCB formula used by parent to select a child.
        This node will be selected by parent with probability proportional
        to its weight."""
        if self.parent is None:
            raise Exception("no")
        explore_val = UCB_CONST * math.sqrt(math.log(self.parent.visits)/self.visits) * ((-1) if side == 1 else 1)
        return self.value + explore_val
