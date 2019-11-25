import agent
import board
import heuristic
from time import time
class MCTS(agent.Agent):
    def __init__(self, side, depth, n_rollouts, variant, use_heuristic):
        self.side = side
        self.depth = depth
        self.n_rollouts = n_rollouts
        self.variant = variant
        self.use_heuristic = use_heuristic

    def get_move(self,chessboard, pos_counts):
        # then = time()
        result = self.alpha_beta(chessboard, pos_counts, 0, -100000, 100000, self.side)[0]
        # now = time()-then
        # print("get_move took " + str(now) + " seconds")
        return result

def MCTS(root):
    for i in range(rollouts):
        cur = root
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
        for move in cur.state.getMoves():
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
    def order_moves_naive(self, chessboard, side):
        '''Given a board and a side, naively orders the set of all possible moves based solely on whether or not they involve the capture of a piece, and if so, how much the piece is worth.'''
        moves = board.get_all_moves(chessboard, side)
        moves_and_values = [(move, heuristic.evaluate(board.make_move(chessboard, move[0], move[1]))) for move in moves]
        moves_and_values.sort(reverse=(side==1), key=lambda x: x[1])
        return [tup[0] for tup in moves_and_values]

class Node(object):
    """Node used in MCTS"""
    
    def __init__(self, state, parent_node):
        """Constructor for a new node representing game state
        state. parent_node is the Node that is the parent of this
        one in the MCTS tree. """
        self.state = state
        self.parent = parent_node
        self.children = {} # maps moves (keys) to Nodes (values); if you use it differently, you must also change addMove
        self.visits = 0
        self.value = float("nan")
        # Note: you may add additional fields if needed
        
    def addMove(self, move):
        """
        Adds a new node for the child resulting from move if one doesn't already exist.
        Returns true if a new node was added, false otherwise.
        """
        if move not in self.children:
            state = self.state.nextState(move)
            self.children[move] = Node(state, self)
            return True
        return False
    
    def getValue(self):
        """
        Gets the value estimate for the current node. Value estimates should correspond
        to the win percentage for the player at this node (accounting for draws as in 
        the project description).
        """
        return self.value

    def updateValue(self, outcome):
        """Updates the value estimate for the node's state.
        outcome: +1 for 1st player win, -1 for 2nd player win, 0 for draw."""
        # NOTE: which outcome is preferred depends on self.state.turn()
        self.value = 0
        if len(self.children) == 0:
            self.value = outcome
        for child in self.children.values():
            self.value += child.value * child.visits
        if self.parent:
            self.parent.updateValue(0)

    def UCBWeightOld(self):
        """Weight from the UCB formula used by parent to select a child.
        This node will be selected by parent with probability proportional
        to its weight."""
        if self.parent is None:
            raise Exception("no")
        explore_val = UCB_CONST * math.sqrt(math.log(self.parent.visits)/self.visits)
        return self.value + explore_val

    def UCBWeight(self):
        """Weight from the UCB formula used by parent to select a child.
        This node will be selected by parent with probability proportional
        to its weight."""
        if self.parent is None:
            raise Exception("no")
        explore_val = UCB_CONST * math.sqrt(math.log(self.parent.visits)/self.visits) * ((-1) if self.state.getTurn() == -1 else 1)
        return self.value + explore_val
