import board
import numpy as np

one_dim_vals = np.array([[0.1, 0.2, 0.3, 1, 1, 0.3, 0.2, 0.1]])
SQUARE_VALS = np.transpose(one_dim_vals) @ one_dim_vals

MOBILITY_SCALAR = np.array([
    0,
    1,
    -1,
    2,
    -2,
    1,
    -1,
    0.3,
    -0.3,
    0.15,
    -0.15,
    -10,
    10
])/5


MATERIAL = np.array([
    0,
    1,
    -1,
    3,
    -3,
    3,
    -3,
    5,
    -5,
    9,
    -9,
    1000,
    -1000
])

def evaluate(chessboard, intricate=False):
    '''Returns a value indicating how favorable the board is for each player. Smaller (more negative) scores favor Black, whereas larger scores favor White.'''
    # C = 0.1
    total = 0
    if intricate:
        king_locs = (board.find_king(chessboard, 1), board.find_king(chessboard, -1))
        if not king_locs[0]:
            return -10000
        elif not king_locs[1]:
            return 10000
    for row in range(8):
        for col in range(8):
            piece = board.piece_at_square(chessboard, row, col)
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
                    side = board.get_side(piece)
                    if intricate:
                        # Value squares close to the enemy king
                        if side == 1:
                            enemy_king_row, enemy_king_col = king_locs[1]
                        else:
                            enemy_king_row, enemy_king_col = king_locs[0]
                    moves = board.get_moves(chessboard, row, col, check_threat=True)
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
    return total
