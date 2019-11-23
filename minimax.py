from chess import *
import AI
import heuristic

class minimax(AI):
	def __init__(self, depth):
		pass
	def get_move(self,board):
		return alpha_beta(board, 0, -100000, 100000, side)[0]





def order_moves_naive(board, side):
    '''Given a board and a side, naively orders the set of all possible moves based solely on whether or not they involve the capture of a piece, and if so, how much the piece is worth.'''
    moves = get_all_moves(board, side)
    moves_and_values = [(move, heuristic.evaluate(make_move(board, move[0], move[1]))) for move in moves]
    moves_and_values.sort(reverse=(side==1), key=lambda x: x[1])
    return [tup[0] for tup in moves_and_values]

def alpha_beta(board, depth, alpha, beta, side):
    '''Given a board and a move, returns an evaluation for that move by recursing over every possible move in each state until the depth limit is reached, then using the evaluate() function and passing the values back up through minimax with alpha-beta pruning.'''
    if has_no_moves(board, 1):
        if test_check(board, 1):
            return (None, -10000)
        else:
            return (None, 0)
    elif has_no_moves(board, -1):
        if test_check(board, -1):
            return (None, 10000)
        else:
            return (None, 0)
    elif depth == MAX_DEPTH:
        value = heuristic.evaluate(board)
        return (None, value)
    #uses naive move ordering instead of alpha-beta, since otherwise it would never stop!    
    ordered_moves = order_moves_naive(board, side)
        
    if side == 1:
        best_move = (None, -100000)
        for move in ordered_moves:
            new_board = make_move(board, move[0], move[1])
            _, move_value = alpha_beta(new_board, depth+1, alpha, beta, -1)
            if move_value > best_move[1]:
                best_move = (move, move_value)
            alpha = max(alpha, best_move[1])
            if beta <= best_move[1]:
                return best_move
        return best_move
    else:
        best_move = (None, 100000)
        for move in ordered_moves:
            new_board = make_move(board, move[0], move[1])
            _, move_value = alpha_beta(new_board, depth+1, alpha, beta, 1)
            if move_value < best_move[1]:
                best_move = (move, move_value)
            beta = min(beta, best_move[1])
            if alpha >= best_move[1]:
                return best_move
        return best_move
    return total