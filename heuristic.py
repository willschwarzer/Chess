import board
import numpy as np

one_dim_vals = np.array([[0.1, 0.2, 0.3, 1, 1, 0.3, 0.2, 0.1]])
square_vals = np.transpose(one_dim_vals) @ one_dim_vals
WHITE_SQUARE_VALS = np.copy(square_vals)
BLACK_SQUARE_VALS = np.copy(square_vals)
for i in range(8):
    WHITE_SQUARE_VALS[i] += (0.5-i/10)
    BLACK_SQUARE_VALS[7-i] += (0.5-i/10)

MOBILITY_SCALAR = np.array([
    0,
    1,
    -1,
    1,
    -1,
    1,
    -1,
    0.3,
    -0.3,
    0.3,
    -0.3,
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

def evaluate(chessboard, disp=False, intricate=False):
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
                # King safety
                if piece == 11:
                    # king safety
                    if row == 7:
                        if col == 1 or col == 6:
                            piece_total += 1
                    else:
                        piece_total -= 1
                elif piece == 12:
                    # king safety
                    if row == 0:
                        if col == 1 or col == 6:
                            piece_total -= 1
                    else: 
                        piece_total += 1
                else:
                    side = board.get_side(piece)
                    moves = board.get_moves(chessboard, row, col, check_threat=True, check_check=True)
                    if intricate:
                        # Value squares close to the enemy king
                        if side == 1:
                            enemy_king_row, enemy_king_col = king_locs[1]
                        else:
                            enemy_king_row, enemy_king_col = king_locs[0]
                        for move in moves:
                            king_proximity = (move[0] - enemy_king_row)**2 + (move[1] - enemy_king_col)**2
                            # 7*7 + 7*7 = 98
                            king_proximity /= 98
                            piece_total += SQUARE_VALS[move]*king_proximity
                    else:
                        for move in moves:
                            if side == 1:
                                piece_total += WHITE_SQUARE_VALS[move]
                            elif side == -1:
                                piece_total += BLACK_SQUARE_VALS[move]
                    # square root to encourage developing all pieces
                    # piece_total = piece_total**(1/3)
                    piece_total *= MOBILITY_SCALAR[piece]
                    if disp:
                        print(piece, 'has mobility', piece_total)
                piece_total += MATERIAL[piece]
                total += piece_total# + C*len(moves)
    return total
