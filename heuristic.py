import board
import numpy as np
from scipy.ndimage import gaussian_filter

# Indicates how important positioning/mobility should be to each piece's
# evaluation
MOBILITY_SCALARS = np.array([
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
])/10

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

def evaluate(chessboard):
    '''Returns a value indicating how favorable the board is for each player.
    Smaller (more negative) scores favor Black, whereas larger scores 
    favor White. Uses square value maps to encourage aggressiveness against
    the enemy king and control of the center.'''
    total = 0
    # Find kings for square valuation (closer to the king is more important)
    king_locs = (board.find_king(chessboard, 1), board.find_king(chessboard, -1))
    white_square_vals, black_square_vals = np.zeros([8, 8]), np.zeros([8, 8])
    # Place value density spikes on the king's position and center squares
    # (will be flattened later using gaussian filter)
    white_square_vals[king_locs[1][0]][king_locs[1][1]] += 100
    white_square_vals[3][3] += 10
    white_square_vals[3][4] += 10
    # SD (second argument) affects how concentrated square valuation should be
    white_square_vals = gaussian_filter(white_square_vals, 1)
    if king_locs[0] is not None:
        # Standard valuation
        black_square_vals[king_locs[0][0]][king_locs[0][1]] -= 100
        black_square_vals[4][3] -= 10
        black_square_vals[4][4] -= 10
    else:
        # Horde valuation (value getting to the back rank)
        black_square_vals[7] -= 100
    black_square_vals = gaussian_filter(black_square_vals, 1)
    # Tally up material and mobility valuations
    for row in range(8):
        for col in range(8):
            piece = board.piece_at_square(chessboard, row, col)
            if piece != 0:
                piece_total = 0
                if piece == 11:
                    # King safety
                    if row == 7:
                        if col == 1 or col == 6:
                            piece_total += 1
                    else:
                        piece_total -= 1
                elif piece == 12:
                    if row == 0:
                        if col == 1 or col == 6:
                            piece_total -= 1
                    else: 
                        piece_total += 1
                else:
                    # Mobility for other pieces
                    side = board.get_side(piece)
                    # For the sake of evaluation speed, don't test for check
                    moves = board.get_moves(chessboard, row, col, check_threat=True, check_check=False)
                    for move in moves:
                        if side == 1:
                            piece_total += white_square_vals[move]
                        elif side == -1:
                            piece_total += black_square_vals[move]
                    # Square root to encourage developing all pieces
                    piece_total = (piece_total**(2))**(1/4)
                    piece_total *= MOBILITY_SCALARS[piece]
                piece_total += MATERIAL[piece]
                total += piece_total
    return total


def order_moves_naive(self, chessboard, side):
    '''Given a board and a side, orders the set of all possible moves 
    based solely on the heuristic evaluation of the resulting board. 
    Intended to optimize alpha-beta. Note that this does not consider 
    game ending moves like checkmate (that would require a call 
    to get_result()).'''
    moves = board.get_all_moves(chessboard, side)
    moves_and_values = [(move, heuristic.evaluate(board.make_move(chessboard, *move))) for move in moves]
    # If minimax is playing White, do descendimg sort, otherwise normal
    moves_and_values.sort(reverse=(side==1), key=lambda x: x[1])
    # Return just the moves
    return [tup[0] for tup in moves_and_values]
