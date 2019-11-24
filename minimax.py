#import chess
import agent
import heuristic
import board

class Minimax(agent.Agent):

    def __init__(self, side, depth):
        self.depth = depth
        self.side = side

    def get_move(self,chessboard):
        return self.alpha_beta(chessboard, 0, -100000, 100000, self.side)[0]

    def order_moves_naive(self, chessboard, side):
        '''Given a board and a side, naively orders the set of all possible moves based solely on whether or not they involve the capture of a piece, and if so, how much the piece is worth.'''
        moves = board.get_all_moves(chessboard, side)
        moves_and_values = [(move, heuristic.evaluate(board.make_move(chessboard, move[0], move[1]))) for move in moves]
        moves_and_values.sort(reverse=(side==1), key=lambda x: x[1])
        return [tup[0] for tup in moves_and_values]

    def alpha_beta(self, chessboard, depth, alpha, beta, side):
        '''Given a board and a move, returns an evaluation for that move by recursing over every possible move in each state until the depth limit is reached, then using the evaluate() function and passing the values back up through minimax with alpha-beta pruning.'''
        if not board.find_king(chessboard, 1):
            return (None, -10000)
        elif not board.find_king(chessboard, -1):
            return (None, 10000)
        # else:
        #     if board.has_no_moves(chessboard, 1):
        #         if board.test_check(chessboard, 1):
        #             return (None, -10000)
        #         else:
        #             return (None, 0)
        #     elif board.has_no_moves(chessboard, -1):
        #         if board.test_check(chessboard, -1):
        #             return (None, 10000)
        #         else:
        #             return (None, 0)
        elif depth == self.depth:
            value = heuristic.evaluate(chessboard)
            return (None, value)
        ordered_moves = self.order_moves_naive(chessboard, side)
            
        if side == 1:
            best_move = (None, -100000)
            for move in ordered_moves:
                new_board = board.make_move(chessboard, move[0], move[1])
                _, move_value = self.alpha_beta(new_board, depth+1, alpha, beta, -1)
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
                _, move_value = self.alpha_beta(new_board, depth+1, alpha, beta, 1)
                if move_value < best_move[1]:
                    best_move = (move, move_value)
                beta = min(beta, best_move[1])
                if alpha >= best_move[1]:
                    return best_move
            return best_move
        return total
