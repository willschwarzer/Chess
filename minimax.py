import numpy as np

import agent
import board
import heuristic
from time import time

class Minimax(agent.Agent):
    ''' Chess agent running standard alpha-beta search.'''
    def __init__(self, side, depth, variant):
        self.depth = depth
        self.side = side
        self.variant = variant

    def get_move(self, chessboard, pos_counts):
        ''' Return a move selected by alpha-beta from current position.'''
        move = self.alpha_beta(chessboard, pos_counts, 0, -100000, 100000, self.side)[0]
        return move

    def alpha_beta(self, chessboard, pos_counts, depth, alpha, beta, side):
        '''Given a board and a move, returns an evaluation for that move by 
        recursing over every possible move in each state until the depth 
        limit is reached, then using the evaluate() function and passing 
        the values back up through minimax with alpha-beta pruning. 
        pos_counts is a position counter used to determine threefold 
        repetition.'''
        result = board.get_result(chessboard, pos_counts, self.variant, -side, False)
        if result is not None:
            # Base case 1: game is over
            return (None, result*100000)
        elif depth == self.depth:
            # Base case 2: max depth
            value = heuristic.evaluate(chessboard)
            return (None, value)
        if depth == self.depth-1:
            ordered_moves = board.get_all_moves(chessboard, side)
        else:
            ordered_moves = heuristic.order_moves_naive(chessboard, side)
        if side == 1:
            best_move = (None, -100000)
            for move in ordered_moves:
                new_board = board.make_move(chessboard, move[0], move[1])
                pos_counts[new_board] += 1
                _, move_value = self.alpha_beta(new_board, pos_counts, depth+1, alpha, beta, -1)
                pos_counts[new_board] -= 1
                # Add noise to make the agent more interesting
                noise = np.random.normal(scale=0.01)
                move_value += noise
                if move_value > best_move[1]:
                    best_move = (move, move_value)
                alpha = max(alpha, best_move[1])
                if beta <= best_move[1]:
                    return best_move
            return best_move
        else:
            best_move = (None, 100000)
            for move in ordered_moves:
                new_board = board.make_move(chessboard, move[0], move[1])
                pos_counts[new_board] += 1
                _, move_value = self.alpha_beta(new_board, pos_counts, depth+1, alpha, beta, 1)
                move_value *= 0.9
                noise = np.random.normal(scale=0.01)
                move_value += noise
                pos_counts[new_board] -= 1
                if move_value < best_move[1]:
                    best_move = (move, move_value)
                beta = min(beta, best_move[1])
                if alpha >= best_move[1]:
                    return best_move
            return best_move
