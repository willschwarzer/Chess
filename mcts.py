import random
from time import time
import pickle

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
            load_root()
        else:
            self.root = Node(board.set_board(variant), None)
            
        self.cur = self.root

    def load_root(self):
        self.root = pickle.load(open(input_path, 'rb'))
    
    def store_root(self):
        if output_path:
            pickle.dump(self.root, open(output_path, 'wb'))

    def get_move(self, chessboard, pos_counts):
        # then = time()
        result = MCTS()
        # now = time()-then
        # print("get_move took " + str(now) + " seconds")
        return result

    def add_move(self, move):
        # TODO
        pass

    def MCTS():
        # TODO
        for i in range(rollouts):
            cur = self.cur
            cur.visits += 1
            while len(cur.children) == len(cur.state.getMoves()) and not cur.state.isTerminal():
                bestChild = list(cur.children.values())[0]
                for child in list(cur.children.values())[1:]:
                    if cur.state.getTurn()*(child.UCBWeight()-bestChild.UCBWeight()) > 0:
                        bestChild = child
                cur = bestChild
                cur.visits += 1
            if cur.state.isTerminal():
                continue
            for move in board.get_all_moves(chessboard, side):
                if cur.addMove(move):
                    break
            expanded = cur.children[move]
            expanded.visits += 1
            outcome = random_to_end(expanded.state)
            expanded.updateValue(outcome)
        
        bestMove = list(root.children.keys())[0]
        for move in root.children:
            child = root.children[move]
            bestChild = root.children[bestMove]
            if root.state.getTurn()*(child.getValue()-bestChild.getValue()) > 0:
                bestMove = move
            
        return bestMove

    def random_to_end(chessboard, pos_counts, side, depth, use_heuristic):
        ''' side: which player's move it is in position chessboard''' 
        result = board.get_result(chessboard, pos_counts, self.variant, side, False)
        if result is not None:
            # Return a large number since we might be stopping early and doing
            # a heuristic evaluation, which might be bigger than 1 or -1
            return result*100000
        elif self.max_depth != 0 and depth == self.max_depth:
            return heuristic.evaluate(chessboard)
        elif use_heuristic:
            move = self.order_moves_naive(chessboard, side)[0] 
        else:
            move = random.shuffle(board.get_all_moves(chessboard, side))[0]
        new_board = board.make_move(chessboard, *move)
        pos_counts[new_board] += 1
        outcome = random_to_end(new_board, pos_counts, side, depth+1, use_heuristic)
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

    def update_value(self, outcome):
        """Updates the value estimate for the node's state.
        outcome: +100000 for a first player win, -100000 for a second player win, 0 for a draw, or some heuristic evaluation in between"""
        # NOTE: which outcome is preferred depends on self.state.turn()
        self.value = 0
        if len(self.children) == 0:
            self.value = outcome
        for child in self.children.values():
            self.value += child.value * child.visits
        if self.parent:
            self.parent.updateValue(0)

    def UCB_weight(self, side):
        """Weight from the UCB formula used by parent to select a child.
        This node will be selected by parent with probability proportional
        to its weight."""
        if self.parent is None:
            raise Exception("no")
        explore_val = UCB_CONST * math.sqrt(math.log(self.parent.visits)/self.visits) * ((-1) if side == 1 else 1)
        return self.value + explore_val
