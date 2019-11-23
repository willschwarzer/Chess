from chess import *



def evaluate(board, intricate=False):
    '''Returns a value indicating how favorable the board is for each player. Smaller (more negative) scores favor Black, whereas larger scores favor White.'''
    # C = 0.1
    total = 0
    if intricate:
        king_locs = (find_king(board, 1), find_king(board, -1))
        if not king_locs[0]:
            return -10000
        elif not king_locs[1]:
            return 10000
    for row in range(8):
        for col in range(8):
            piece = piece_at_square(board, row, col)
            if piece != 0:
                piece_total = 0
                if piece == 11:
                    # king safety
                    if row == 7:
                        if col == 1 or col == 6:
                            piece_total = 1
                        elif col == 2:
                            piece_total = 0.75
                    else: 
                        piece_total = 0.5
                elif piece == 12:
                    # king safety
                    if row == 1:
                        if col == 1 or col == 6:
                            piece_total += 1
                        elif col == 2:
                            piece_total += 0.75
                    else: 
                        piece_total = -1
                else:
                    side = get_side(piece)
                    if intricate:
                        # Value squares close to the enemy king
                        if side == 1:
                            enemy_king_row, enemy_king_col = king_locs[1]
                        else:
                            enemy_king_row, enemy_king_col = king_locs[0]
                    moves = get_moves(board, row, col, check_threat=True)
                    if intricate:
                        for move in moves:
                            king_proximity = (move[0] - enemy_king_row)**2 + (move[1] - enemy_king_col)**2
                            # 7*7 + 7*7 = 98
                            king_proximity /= 98
                            piece_total += SQUARE_VALS[move]*king_proximity
                    else:
                        for move in moves:
                            piece_total += SQUARE_VALS[move]
                    # square root to encourage developing all pieces
                    # piece_total = piece_total**(1/3)
                    piece_total *= MOBILITY_SCALAR[piece]
                piece_total += MATERIAL[piece]
                total += piece_total# + C*len(moves)




def order_moves_naive(board, side):
    '''Given a board and a side, naively orders the set of all possible moves based solely on whether or not they involve the capture of a piece, and if so, how much the piece is worth.'''
    moves = get_all_moves(board, side)
    moves_and_values = [(move, evaluate(make_move(board, move[0], move[1]))) for move in moves]
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
        value = evaluate(board)
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