'''
Authors: Will Schwarzer
Date: November 23, 2019
Stores functions and constants relating to the chess board.
'''

import numpy as np

EMPTY=0
WHITE_PAWN=1
BLACK_PAWN=2
WHITE_KNIGHT=3
BLACK_KNIGHT=4
WHITE_BISHOP=5
BLACK_BISHOP=6
WHITE_ROOK=7
BLACK_ROOK=8
WHITE_QUEEN=9
BLACK_QUEEN=10
WHITE_KING=11
BLACK_KING=12

# See set_board() for an explanation of these digits
WHITE_CASTLE_DIGIT = 64
BLACK_CASTLE_DIGIT = 65
EP_ROW_DIGIT = 66
EP_COL_DIGIT = 67

NUM_PIECES = 13

POWERS = np.array([NUM_PIECES**n for n in range(70)])

def set_board(variant='normal'):
    ''' Represented digitally: each square is a place, counting horizontally
    from the upper left, and each piece is an enum;
    64th and 65th digits are castling rights for white and black, respectively
    (0 for neither side, 1 for kingside only, 2 for queenside only, 3 for both)
    66th and 67th digits are row and col, respectively, for the square with
    legal en passant, if any; they're set to 8 if there is no such square
    If n is number of pieces:
    board = ep_col * n^67 + ep_col * n^66
    +
    black_castle_rights * n^65 + white_castle_rights * n^64
    +
    sum from i=0 to 63 of piece_i * n^i
    '''
    board = 0
    if variant == 'normal':
        # Pawns
        for col in range(8):
            place = 1*8 + col
            board += BLACK_PAWN*POWERS[place]
            place = 6*8 + col
            board += WHITE_PAWN*POWERS[place]
        # Knights
        for col in (1, 6):
            place = 0*8 + col
            board += BLACK_KNIGHT*POWERS[place]
            place = 7*8 + col
            board += WHITE_KNIGHT*POWERS[place]
        # Bishops
        for col in (2, 5):
            place = 0*8 + col
            board += BLACK_BISHOP*POWERS[place]
            place = 7*8 + col
            board += WHITE_BISHOP*POWERS[place]
        # Rooks
        for col in (0, 7):
            place = 0*8 + col
            board += BLACK_ROOK*POWERS[place]
            place = 7*8 + col
            board += WHITE_ROOK*POWERS[place]
        # Queens
        place = 0*8 + 3
        board += BLACK_QUEEN*POWERS[place]
        place = 7*8 + 3
        board += WHITE_QUEEN*POWERS[place]

        # Kings
        place = 0*8 + 4
        board += BLACK_KING*POWERS[place]
        place = 7*8 + 4
        board += WHITE_KING*POWERS[place]
        # Castling: both sides start at 3, i.e. can castle either side
        board += 3*POWERS[WHITE_CASTLE_DIGIT]
        board += 3*POWERS[BLACK_CASTLE_DIGIT]
    elif variant == 'horde':
        # Pawns
        for col in range(8):
            place = 1*8 + col
            board += BLACK_PAWN*POWERS[place]
        # Knights
        for col in (1, 6):
            place = 0*8 + col
            board += BLACK_KNIGHT*POWERS[place]
        # Bishops
        for col in (2, 5):
            place = 0*8 + col
            board += BLACK_BISHOP*POWERS[place]
        # Rooks
        for col in (0, 7):
            place = 0*8 + col
            board += BLACK_ROOK*POWERS[place]
        # Queens
        place = 0*8 + 3
        board += BLACK_QUEEN*POWERS[place]
        # Kings
        place = 0*8 + 4
        board += BLACK_KING*POWERS[place]
        # White pawns
        for row in range(4, 8):
            for col in range(8):
                place = row*8 + col
                board += WHITE_PAWN*POWERS[place]
        for col in (1, 2, 5, 6):
            place = 3*8 + col
            board += WHITE_PAWN*POWERS[place]
        # Castling: Only black can castle (not that it matters)
        board += 3*POWERS[BLACK_CASTLE_DIGIT]
    elif variant == 'test':
        place = 3*8 + 3
        board += BLACK_PAWN*POWERS[place]
        place = 6*8 + 4
        board += WHITE_PAWN*POWERS[place]
        place = 0*8 + 3
        board += BLACK_KING*POWERS[place]
        place = 7*8 + 4
        board += WHITE_KING*POWERS[place]
        # No castling
    # En passant initialized to nonexistent, i.e. row, col = 8, 8
    place = 66
    board += 8*POWERS[EP_ROW_DIGIT]
    place = 67
    board += 8*POWERS[EP_COL_DIGIT]
    return board

def get_ep_square(board):
    row = (board // POWERS[EP_ROW_DIGIT]) % NUM_PIECES
    col = (board // POWERS[EP_COL_DIGIT]) % NUM_PIECES
    return (row, col)

def set_ep_square(board, row, col):
    board -= ((board // POWERS[EP_ROW_DIGIT]) %  NUM_PIECES)*POWERS[EP_ROW_DIGIT]
    board -= ((board // POWERS[EP_COL_DIGIT]) %  NUM_PIECES)*POWERS[EP_COL_DIGIT]
    board += row*POWERS[EP_ROW_DIGIT]
    board += col*POWERS[EP_COL_DIGIT]
    return board

def reset_ep_square(board):
    return set_ep_square(board, 8, 8)

def get_castling_rights(board, side):
    if side == 1:
        castle_digit = WHITE_CASTLE_DIGIT
    else:
        castle_digit = BLACK_CASTLE_DIGIT
    return (board // POWERS[castle_digit]) % NUM_PIECES

def remove_castling_rights(board, side, castle_side):
    if side == 1:
        castle_digit = WHITE_CASTLE_DIGIT
    else:
        castle_digit = BLACK_CASTLE_DIGIT
    castle_rights = (board // POWERS[castle_digit]) % NUM_PIECES
    new_castle_rights = castle_rights
    # Kingside
    if castle_side == 1:
        if castle_rights == 3:
            new_castle_rights = 2
        elif castle_rights == 1:
            new_castle_rights = 0
    # Queenside
    else:
        if castle_rights == 3:
            new_castle_rights = 1
        elif castle_rights == 2:
            new_castle_rights = 0
    diff = new_castle_rights - castle_rights
    return board + diff*POWERS[castle_digit]

def promote(board, side, col):
    if side == 1:
        row = 0
    else:
        row = 7
    square = row*8 + col
    # Piece at this square is a pawn
    # For now, just put a queen there
    # 8  = 9 - 1 = queen - pawn
    # 8 = 10 - 2 = queen - pawn
    board += 8 * POWERS[square]
    return board

def piece_at_square(board, row, col):
    if not in_bounds(row, col):
        return None
    square = row*8 + col
    return (board // POWERS[square]) % NUM_PIECES

def square_is_empty(board, row, col):
    return (not piece_at_square(board, row, col))

def get_side(piece):
    if piece is None or piece == 0:
        return None
    if piece % 2 == 0:
        return -1
    else:
        return 1

def make_move(board, start, finish):
    piece = piece_at_square(board, *start)
    # Note whether or not we're doing ep
    is_ep = ((piece == 1 or piece == 2) and finish == get_ep_square(board))
    # If there was en passant possible at a square, make it impossible
    board = reset_ep_square(board)
    # If moving a pawn two squares, put in the ep
    # White pawn special rules
    if piece == 1:
        if finish[0] == start[0] - 2:
            board = set_ep_square(board, start[0]-1, start[1])
    # Black pawn
    elif piece == 2:
        if finish[0] == start[0] + 2:
            board = set_ep_square(board, start[0]+1, start[1])
    # If moving a rook, remove those castling rights
    # White kingside rook
    if start == (7, 7):
        board = remove_castling_rights(board, 1, 1)
    # White queenside rook
    elif start == (7, 0):
        board = remove_castling_rights(board, 1, -1)
    # Black kingside rook
    elif start == (0, 7):
        board = remove_castling_rights(board, -1, 1)
    # Black queenside rook
    elif start == (0, 0):
        board = remove_castling_rights(board, -1, -1)
    # If moving a king, remove all castling rights
    if piece == 11:
        board = remove_castling_rights(board, 1, 1)
        board = remove_castling_rights(board, 1, -1)
    elif piece == 12:
        board = remove_castling_rights(board, -1, 1)
        board = remove_castling_rights(board, -1, -1)
    start_square = start[0]*8 + start[1]
    finish_square = finish[0]*8 + finish[1]
    if piece_at_square(board, *finish) is None:
        breakpoint()
    diff = piece*POWERS[finish_square] - \
            piece*POWERS[start_square] - \
            piece_at_square(board, *finish)*POWERS[finish_square]
    if is_ep:
        # White pawn: get rid of black pawn below it
        if piece == 1:
            removed_square = finish_square+8
            diff -= 2*POWERS[removed_square]
        # Black pawn: get rid of white pawn above it
        else:
            removed_square = finish_square-8
            diff -= 1*POWERS[removed_square]
    # Deal with castling by also moving the rook
    elif piece == 11:
        # White castling kingside
        if finish[1] == start[1]+2:
            old_rook_square = finish_square+1
            new_rook_square = finish_square-1
            diff += 7*(POWERS[new_rook_square] - POWERS[old_rook_square])
        # White castling queenside
        elif finish[1] == start[1]-2:
            old_rook_square = finish_square-2
            new_rook_square = finish_square+1
            diff += 7*(POWERS[new_rook_square] - POWERS[old_rook_square])
    elif piece == 12:
        # Black castling kingside
        if finish[1] == start[1]+2:
            old_rook_square = finish_square+1
            new_rook_square = finish_square-1
            diff += 8*(POWERS[new_rook_square] - POWERS[old_rook_square])
        # Black castling queenside
        elif finish[1] == start[1]-2:
            old_rook_square = finish_square-2
            new_rook_square = finish_square+1
            diff += 8*(POWERS[new_rook_square] - POWERS[old_rook_square])

    board = board + diff
    # Deal with promotion/en passant
    # White pawn
    if piece == 1:
        if finish[0] == 0:
            board = promote(board, 1, finish[1])
    # Black pawn
    elif piece == 2:
        if finish[0] == 7:
            board = promote(board, -1, finish[1])
    return board

def find_king(board, side):
    if side == 1:
        king = WHITE_KING
    else:
        king = BLACK_KING
    for row in range(8):
        for col in range(8):
            if king == piece_at_square(board, row, col):
                return (row, col)
    return None

def test_check(board, side):
    king_square = find_king(board, side)
    if not king_square:
        return False
    # for row in range(8):
    #     for col in range(8):
    #         piece = piece_at_square(board, row, col)
    #         if piece != 0 and get_side(piece) != side:
    #             if king_square in get_moves(board, row, col, True):
    #                 return True
    # return False

    # Test upper left diag
    row = king_square[0]-1
    col = king_square[1]-1
    piece = piece_at_square(board, row, col)
    if side == 1:
        if piece == BLACK_KING:
            return True
    else:
        if piece == WHITE_KING:
            return True
    while piece == 0:
        col -= 1
        row -= 1
        piece = piece_at_square(board, row, col)
    if side == 1:
        if piece == BLACK_BISHOP or piece == BLACK_QUEEN:
            return True
    else:
        if piece == WHITE_BISHOP or piece == WHITE_QUEEN:
            return True
    # Test upper right diag
    row = king_square[0]-1
    col = king_square[1]+1
    piece = piece_at_square(board, row, col)
    if side == 1:
        if piece == BLACK_KING:
            return True
    else:
        if piece == WHITE_KING:
            return True
    while piece == 0:
        col += 1
        row -= 1
        piece = piece_at_square(board, row, col)
    if side == 1:
        if piece == BLACK_BISHOP or piece == BLACK_QUEEN:
            return True
    else:
        if piece == WHITE_BISHOP or piece == WHITE_QUEEN:
            return True
    # Test lower left diag
    row = king_square[0]+1
    col = king_square[1]-1
    piece = piece_at_square(board, row, col)
    if side == 1:
        if piece == BLACK_KING:
            return True
    else:
        if piece == WHITE_KING:
            return True
    while piece == 0:
        col -= 1
        row += 1
        piece = piece_at_square(board, row, col)
    if side == 1:
        if piece == BLACK_BISHOP or piece == BLACK_QUEEN:
            return True
    else:
        if piece == WHITE_BISHOP or piece == WHITE_QUEEN:
            return True
    # Test lower left diag
    row = king_square[0]+1
    col = king_square[1]+1
    piece = piece_at_square(board, row, col)
    if side == 1:
        if piece == BLACK_KING:
            return True
    else:
        if piece == WHITE_KING:
            return True
    while piece == 0:
        col += 1
        row += 1
        piece = piece_at_square(board, row, col)
    if side == 1:
        if piece == BLACK_BISHOP or piece == BLACK_QUEEN:
            return True
    else:
        if piece == WHITE_BISHOP or piece == WHITE_QUEEN:
            return True

    # Test col above
    row = king_square[0]-1
    col = king_square[1]
    piece = piece_at_square(board, row, col)
    if side == 1:
        if piece == BLACK_KING:
            return True
    else:
        if piece == WHITE_KING:
            return True
    while piece == 0:
        row -= 1
        piece = piece_at_square(board, row, col)
    if side == 1:
        if piece == BLACK_ROOK or piece == BLACK_QUEEN:
            return True
    else:
        if piece == WHITE_ROOK or piece == WHITE_QUEEN:
            return True
    # Test col below
    row = king_square[0]+1
    col = king_square[1]
    piece = piece_at_square(board, row, col)
    if side == 1:
        if piece == BLACK_KING:
            return True
    else:
        if piece == WHITE_KING:
            return True
    while piece == 0:
        row += 1
        piece = piece_at_square(board, row, col)
    if side == 1:
        if piece == BLACK_ROOK or piece == BLACK_QUEEN:
            return True
    else:
        if piece == WHITE_ROOK or piece == WHITE_QUEEN:
            return True
    # Test row to the left
    row = king_square[0]
    col = king_square[1]-1
    piece = piece_at_square(board, row, col)
    if side == 1:
        if piece == BLACK_KING:
            return True
    else:
        if piece == WHITE_KING:
            return True
    while piece == 0:
        col -= 1
        piece = piece_at_square(board, row, col)
    if side == 1:
        if piece == BLACK_ROOK or piece == BLACK_QUEEN:
            return True
    else:
        if piece == WHITE_ROOK or piece == WHITE_QUEEN:
            return True
    # Test row to the right
    row = king_square[0]
    col = king_square[1]+1
    piece = piece_at_square(board, row, col)
    if side == 1:
        if piece == BLACK_KING:
            return True
    else:
        if piece == WHITE_KING:
            return True
    while piece == 0:
        col += 1
        piece = piece_at_square(board, row, col)
    if side == 1:
        if piece == BLACK_ROOK or piece == BLACK_QUEEN:
            return True
    else:
        if piece == WHITE_ROOK or piece == WHITE_QUEEN:
            return True
    row = king_square[0]
    col = king_square[1]
    knight_squares = [move for move in get_moves_knight(board, row, col) if in_bounds(*move)]
    if side == 1:
        for square in knight_squares:
            if piece_at_square(board, *square) == BLACK_KNIGHT:
                return True
    else:
        for square in knight_squares:
            if piece_at_square(board, *square) == WHITE_KNIGHT:
                return True
    if side == 1:
        if piece_at_square(board, row-1, col-1) == BLACK_PAWN:
            return True
        elif piece_at_square(board, row-1, col+1) == BLACK_PAWN:
            return True
    else:
        if piece_at_square(board, row+1, col-1) == WHITE_PAWN:
            return True
        elif piece_at_square(board, row+1, col+1) == WHITE_PAWN:
            return True
    return False


def in_bounds(row, col):
    return (0 <= row <= 7) and (0 <= col <= 7)

def is_legal(board, start, finish, check_threat=False, check_check=False):
    ''' Returns a piece-independent evaluation of whether or not a given
    move is legal. Easily extended to different rulesets, such as antichess.
    If check_threat is true, then checks whether or not the given piece
    threatens the square (e.g., this will be true if it has a friend there.)'''
    if not in_bounds(*finish):
        return False
    # If we're just checking threat, we don't care about being in check
    if check_threat:
        return True
    side = get_side(piece_at_square(board, *start))
    if get_side(piece_at_square(board, *finish)) == side:
        return False
    # If it results in a check for the player making the move, nope on out
    if check_check and test_check(make_move(board, start, finish), side):
        return False
    return True

def get_moves(board, row, col, check_threat=False, check_check=False):
    piece = piece_at_square(board, row, col)
    if not piece:
        return []
    if piece in (1, 2):
        moves = get_moves_pawn(board, row, col, check_threat)
    elif piece in (3, 4):
        moves = get_moves_knight(board, row, col, check_threat)
    elif piece in (5, 6):
        moves = get_moves_bishop(board, row, col, check_threat)
    elif piece in (7, 8):
        moves = get_moves_rook(board, row, col, check_threat)
    elif piece in (9, 10):
        moves = get_moves_queen(board, row, col, check_threat)
    else:
        moves = get_moves_king(board, row, col, check_threat)
    return [move for move in moves if is_legal(board, (row, col), move, check_threat, check_check)]

def get_moves_pawn(board, row, col, check_threat=False, test_check=False):
    side = get_side(piece_at_square(board, row, col))
    ep_square = get_ep_square(board)
    moves = []
    if side == 1:
        if check_threat:
            return [move for move in [(row-1, col-1), (row-1, col+1)] if is_legal(board, (row, col), move, True)]
        # going up
        if row == 6:
            if square_is_empty(board, row-1, col) and square_is_empty(board, row-2, col):
                moves.append((row-2, col))
        if square_is_empty(board, row-1, col):
            moves.append((row-1, col))
        if get_side(piece_at_square(board, row-1, col-1)) == -1:
            moves.append((row-1, col-1))
        if get_side(piece_at_square(board, row-1, col+1)) == -1:
            moves.append((row-1, col+1))
        if ep_square == (row-1, col-1) or ep_square == (row-1, col+1):
            moves.append(ep_square)
        # TODO might be a little slower than doing the logic in the if statement
    else:
        if check_threat:
            return [move for move in [(row+1, col-1), (row+1, col+1)] if is_legal(board, (row, col), move, True)]
        # going down
        if row == 1:
            if square_is_empty(board, row+1, col) and square_is_empty(board, row+2, col):
                moves.append((row+2, col))
        if square_is_empty(board, row+1, col):
            moves.append((row+1, col))
        if get_side(piece_at_square(board, row+1, col-1)) == 1:
            moves.append((row+1, col-1))
        if get_side(piece_at_square(board, row+1, col+1)) == 1:
            moves.append((row+1, col+1))
        if ep_square == (row+1, col-1) or ep_square == (row+1, col+1):
            moves.append(ep_square)

    return moves

def get_moves_knight(board, row, col, check_threat=False):
    side = get_side(piece_at_square(board, row, col))
    moves = [(row+2, col-1),(row+2, col+1),(row+1,col-2), (row+1,col+2),(row-1,col-2),(row-1,col+2),(row-2,col-1),(row-2, col+1)]
    return moves

def get_moves_bishop(board, row, col, check_threat=False):
    side = get_side(piece_at_square(board, row, col))
    moves = [(row+1, col+1), (row+1, col-1), (row-1, col+1), (row-1, col-1)]
    i = 1
    while in_bounds(row+i, col+i) and not piece_at_square(board, row+i, col+i):
        i += 1
        moves.append((row+i, col+i))
    i = 1
    while in_bounds(row+i, col-i) and not piece_at_square(board, row+i, col-i):
        i += 1
        moves.append((row+i, col-i))
    i = 1
    while in_bounds(row-i, col+i) and not piece_at_square(board, row-i, col+i):
        i += 1
        moves.append((row-i, col+i))
    i = 1
    while in_bounds(row-i, col-i) and not piece_at_square(board, row-i, col-i):
        i += 1
        moves.append((row-i, col-i))
    return moves

def get_moves_rook(board, row, col, check_threat=False):
    side = get_side(piece_at_square(board, row, col))
    moves = [(row+1, col), (row, col-1), (row, col+1), (row-1, col)]
    i = 1
    while in_bounds(row+i, col) and not piece_at_square(board, row+i, col):
        i += 1
        moves.append((row+i, col))
    i = 1
    while in_bounds(row-i, col) and not piece_at_square(board, row-i, col):
        i += 1
        moves.append((row-i, col))
    i = 1
    while in_bounds(row, col+i) and not piece_at_square(board, row, col+i):
        i += 1
        moves.append((row, col+i))
    i = 1
    while in_bounds(row, col-i) and not piece_at_square(board, row, col-i):
        i += 1
        moves.append((row, col-i))
    return moves

def get_moves_queen(board, row, col, check_threat=False):
    side = get_side(piece_at_square(board, row, col))
    diags = get_moves_bishop(board, row, col, check_threat)
    orthogs = get_moves_rook(board, row, col, check_threat)
    return diags + orthogs

def get_moves_king(board, row, col, check_threat=False):
    side = get_side(piece_at_square(board, row, col))
    moves = [(row, col+1), (row+1,col), (row+1, col+1), (row-1, col),(row,col-1), (row-1, col-1), (row+1, col-1), (row-1, col+1)]
    # Castling
    castle_rights = get_castling_rights(board, side)
    if not check_threat and not test_check(board, side):
        if castle_rights == 1 or castle_rights == 3:
            if square_is_empty(board, row, col+1) and square_is_empty(board, row, col+2):
                if (col+1 == 8):
                    breakpoint()
                if not test_check(make_move(board, (row, col), (row, col+1)), side):
                    moves.append((row, col+2))
        if castle_rights == 2 or castle_rights == 3:
            if all([square_is_empty(board, row, col-i) for i in range(1, 4)]):
                if not test_check(make_move(board, (row, col), (row, col-1)), side):
                    moves.append((row, col-2))
    return moves

def has_no_moves(board, side):
    for row in range(8):
        for col in range(8):
            if get_side(piece_at_square(board, row, col)) == side:
                # print(get_moves(board, row, col, check_check=True))
                if get_moves(board, row, col, check_check=True):
                    return False
    return True


def get_all_moves(board, side):
    moves = []
    for row in range(8):
        for col in range(8):
            if get_side(piece_at_square(board, row, col)) == side:
                for move in get_moves(board, row, col, False, True):
                    moves.append(((row, col), move))
    return moves



def make_AI_move(board, side, AI_agent):
    #move = alpha_beta(board, 0, -100000, 100000, side)[0]
    move = AI_agent.make_move(board, side)
    return make_move(board, move[0], move[1])

def print_board(board):
    ''' For debugging: just prints all pieces on the board in numeric form'''
    for row in range(8):
        for col in range(8):
            print(piece_at_square(board, row, col), end=' ')
        print()

def get_result(board, pos_counts, variant, side, print_result=True):
    if has_no_moves(board, -side):
        if test_check(board, -side):
            if print_result:
                print('{} wins!'.format('White' if side == 1 else 'Black'))
            return 1
        elif side == -1 and variant == 'horde':
            if print_result:
                print('Black wins!')
            return -1
        else:
            if print_result:
                print('Stalemate.')
            return 0
        # wait for human to click?
    elif pos_counts[board] == 3:
        if print_result:
            print('Draw by threefold repetition.')
        return 0
    elif sum(pos_counts.values()) >= 200:
        if print_result:
            print('Draw by being a really long game.')
        return 0
    return None

