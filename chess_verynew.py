import argparse
import pygame
from enum import Enum
import sys
import time
import cProfile

PIECE_IMGS = [
    None,
    pygame.image.load("images/whitepawn.png"),
    pygame.image.load("images/blackpawn.png"),
    pygame.image.load("images/whiteknight.png"),
    pygame.image.load("images/blackknight.png"),
    pygame.image.load("images/whitebishop.png"),
    pygame.image.load("images/blackbishop.png"),
    pygame.image.load("images/whiterook.png"),
    pygame.image.load("images/blackrook.png"),
    pygame.image.load("images/whitequeen.png"),
    pygame.image.load("images/blackqueen.png"),
    pygame.image.load("images/whiteking.png"),
    pygame.image.load("images/blackking.png")
]
BOARD_IMG = pygame.image.load("images/chessboard.jpg")
HIGHLIGHT_IMG = pygame.image.load("images/highlight.png")

POWERS = [len(piece)**num for num in range(70)]

# See set_board() for an explanation of these digits
WHITE_CASTLE_DIGIT = 64
BLACK_CASTLE_DIGIT = 65
EP_ROW_DIGIT = 66
EP_COL_DIGIT = 67
INSIG_MOD_N_DIGIT = 68
INSIG_DIV_N_DIGIT = 69

# BOARD_SCALE = 1
# MAX_DEPTH = 1
# VARIANT = 'normal'

MATERIAL = [
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
]

class Piece(Enum):
    empty=0
    white_pawn=1
    black_pawn=2
    white_knight=3
    black_knight=4
    white_bishop=5
    black_bishop=6
    white_rook=7
    black_rook=8
    white_queen=9
    black_queen=10
    white_king=11
    black_king=12

def set_board(variant='normal'):
    ''' Represented digitally: each square is a place, counting horizontally
    from the upper left, and each piece is an enum;
    64th and 65th digits are castling rights for white and black, respectively
    (0 for neither side, 1 for kingside only, 2 for queenside only, 3 for both)
    66th and 67th digits are row and col, respectively, for the square with
    legal en passant, if any; they're set to 8 if there is no such square
    68th and 69th digits are the number of turns since the last significant
    move (as usual, defined as a capture or pawn push)
    If n is number of pieces:
    board = num_insignificant_moves/n * n^69 + num_insignificant_moves % n *n^68
    + 
    ep_col * n^67 + ep_col * n^66
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
            board += Piece.black_pawn.value*(len(Piece)**place)
            place = 6*8 + col
            board += Piece.white_pawn.value*(len(Piece)**place)
        # Knights
        for col in (1, 6):
            place = 0*8 + col
            board += Piece.black_knight.value*(len(Piece)**place)
            place = 7*8 + col
            board += Piece.white_knight.value*(len(Piece)**place)
        # Bishops
        for col in (2, 5):
            place = 0*8 + col
            board += Piece.black_bishop.value*(len(Piece)**place)
            place = 7*8 + col
            board += Piece.white_bishop.value*(len(Piece)**place)
        # Rooks
        for col in (0, 7):
            place = 0*8 + col
            board += Piece.black_rook.value*(len(Piece)**place)
            place = 7*8 + col
            board += Piece.white_rook.value*(len(Piece)**place)
        # Queens
        place = 0*8 + 3
        board += Piece.black_queen.value*(len(Piece)**place)
        place = 7*8 + 3
        board += Piece.white_queen.value*(len(Piece)**place)
        # Kings
        place = 0*8 + 4
        board += Piece.black_king.value*(len(Piece)**place)
        place = 7*8 + 4
        board += Piece.white_king.value*(len(Piece)**place)
        # Castling: both sides start at 3, i.e. can castle either side
        board += 3*(len(Piece)**WHITE_CASTLE_DIGIT)
        board += 3*(len(Piece)**BLACK_CASTLE_DIGIT)
    elif variant == 'test':
        place = 3*8 + 3
        board += Piece.black_pawn.value*(len(Piece)**place)
        place = 6*8 + 4
        board += Piece.white_pawn.value*(len(Piece)**place)
        place = 0*8 + 3
        board += Piece.black_king.value*(len(Piece)**place)
        place = 7*8 + 4
        board += Piece.white_king.value*(len(Piece)**place)
        # No castling
    # En passant initialized to nonexistent, i.e. row, col = 8, 8
    place = 66
    board += 8*(len(Piece)**EP_ROW_DIGIT)
    place = 67
    board += 8*(len(Piece)**EP_COL_DIGIT)
    # num_insignificant_moves starts at 0, i.e. is 0 / n and 0 % n
    return board

def reset_insignificant_moves(board):
    return board % (len(Piece)**INSIG_MOD_N_DIGIT)

def increment_insignificant_moves(board):
    return board + (len(Piece)**INSIG_MOD_N_DIGIT)

def get_insignificant_moves(board):
    return board // (len(Piece)**INSIG_MOD_N_DIGIT)

def get_ep_square(board):
    row = (board // (len(Piece)**EP_ROW_DIGIT)) % len(Piece)
    col = (board // (len(Piece)**EP_COL_DIGIT)) % len(Piece)
    return (row, col)

def set_ep_square(board, row, col):
    board -= ((board // (len(Piece)**EP_ROW_DIGIT)) %  len(Piece))*len(Piece)**EP_ROW_DIGIT
    board -= ((board // (len(Piece)**EP_COL_DIGIT)) %  len(Piece))*len(Piece)**EP_COL_DIGIT
    board += row*len(Piece)**EP_ROW_DIGIT
    board += col*len(Piece)**EP_COL_DIGIT
    return board

def reset_ep_square(board):
    return set_ep_square(board, 8, 8)

def get_castling_rights(board, side):
    if side == 1:
        castle_digit = WHITE_CASTLE_DIGIT
    else:
        castle_digit = BLACK_CASTLE_DIGIT
    return (board // len(Piece)**castle_digit) % len(Piece)

def remove_castling_rights(board, side, castle_side):
    if side == 1:
        castle_digit = WHITE_CASTLE_DIGIT
    else:
        castle_digit = BLACK_CASTLE_DIGIT
    castle_rights = (board // len(Piece)**castle_digit) % len(Piece)
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
    return board + diff*len(Piece)**castle_digit

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
    board += 8 * len(Piece)**square
    return board

def piece_at_square(board, row, col):
    if not in_bounds(row, col):
        return None
    square = row*8 + col
    return (board // (len(Piece)**square)) % len(Piece)

def square_is_empty(board, row, col):
    return (not piece_at_square(board, row, col))

def get_side(piece):
    if piece is None or piece == 0:
        return None
    if piece % 2 == 0:
        return -1
    else:
        return 1

def get_type(piece):
    if not piece:
        return None
    if piece in (1, 2):
        return 'pawn'
    if piece in (3, 4):
        return 'knight'
    if piece in (5, 6):
        return 'bishop'
    if piece in (7, 8):
        return 'rook'
    if piece in (9, 10):
        return 'queen'
    return 'king'

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
    diff = piece*(len(Piece)**finish_square) - \
            piece*(len(Piece)**start_square) - \
            piece_at_square(board, *finish)*(len(Piece)**finish_square)
    if is_ep:
        # White pawn: get rid of black pawn below it
        if piece == 1:
            removed_square = finish_square+8
            diff -= 2*len(Piece)**removed_square
        # Black pawn: get rid of white pawn above it
        else:
            removed_square = finish_square-8
            diff -= 1*len(Piece)**removed_square
    # Deal with castling by also moving the rook
    elif piece == 11:
        # White castling kingside
        if finish[1] == start[1]+2:
            old_rook_square = finish_square+1
            new_rook_square = finish_square-1
            diff += 7*(len(Piece)**new_rook_square-len(Piece)**old_rook_square)
        # White castling queenside
        elif finish[1] == start[1]-2:
            old_rook_square = finish_square-2
            new_rook_square = finish_square+1
            diff += 7*(len(Piece)**new_rook_square-len(Piece)**old_rook_square)
    elif piece == 12:
        # Black castling kingside
        if finish[1] == start[1]+2:
            old_rook_square = finish_square+1
            new_rook_square = finish_square-1
            diff += 8*(len(Piece)**new_rook_square-len(Piece)**old_rook_square)
        # Black castling queenside
        elif finish[1] == start[1]-2:
            old_rook_square = finish_square-2
            new_rook_square = finish_square+1
            diff += 8*(len(Piece)**new_rook_square-len(Piece)**old_rook_square)

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
        king = Piece.white_king.value
    else:
        king = Piece.black_king.value
    for row in range(8):
        for col in range(8):
            if king == piece_at_square(board, row, col):
                return (row, col)
    return None

def test_check(board, side):
    king_square = find_king(board, side)
    for row in range(8):
        for col in range(8):
            piece = piece_at_square(board, row, col)
            if piece != 0 and get_side(piece) != side:
                if king_square in get_moves(board, row, col, True):
                    return True
    return False

def in_bounds(row, col):
    return (0 <= row <= 7) and (0 <= col <= 7)

def is_legal(board, start, finish, check_threat=False):
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
    if test_check(make_move(board, start, finish), side):
        return False
    return True

def get_moves(board, row, col, check_threat=False):
    piece = piece_at_square(board, row, col)
    if not piece:
        return []
    if piece in (1, 2):
        return get_moves_pawn(board, row, col, check_threat)
    if piece in (3, 4):
        return get_moves_knight(board, row, col, check_threat)
    if piece in (5, 6):
        return get_moves_bishop(board, row, col, check_threat)
    if piece in (7, 8):
        return get_moves_rook(board, row, col, check_threat)
    if piece in (9, 10):
        return get_moves_queen(board, row, col, check_threat)
    return get_moves_king(board, row, col, check_threat)

def get_moves_pawn(board, row, col, check_threat=False):
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

    return [move for move in moves if is_legal(board, (row, col), move)]

def get_moves_knight(board, row, col, check_threat=False):
    side = get_side(piece_at_square(board, row, col))
    moves = [(row+2, col-1),(row+2, col+1),(row+1,col-2), (row+1,col+2),(row-1,col-2),(row-1,col+2),(row-2,col-1),(row-2, col+1)]
    return [move for move in moves if is_legal(board, (row, col), move, check_threat)]

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
    return [move for move in moves if is_legal(board, (row, col), move, check_threat)]

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
    return [move for move in moves if is_legal(board, (row, col), move, check_threat)]

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
                if not test_check(make_move(board, (row, col), (row, col+1)), side):
                    moves.append((row, col+2))
        if castle_rights == 2 or castle_rights == 3:
            if square_is_empty(board, row, col-1) and square_is_empty(board, row, col-2) and square_is_empty(board, row, col-3):
                if not test_check(make_move(board, (row, col), (row, col-1)), side):
                    moves.append((row, col-2))
    return [move for move in moves if is_legal(board, (row, col), move, check_threat)]

def has_no_moves(board, side):
    for row in range(8):
        for col in range(8):
            if get_side(piece_at_square(board, row, col)) == side:
                if get_moves(board, row, col):
                    return False
    return True

num_evaluations = 0
eval_time_start = 0
eval_time_end = 0
moves_time_start = 0
moves_time_end = 0

def evaluate(board):
    '''Returns a value between (approximately) -1000 and 1000 indicating how favorable the board is for each player. Smaller (more negative) scores favor Black, whereas larger scores favor White.'''
    global num_evaluations, eval_time_start, eval_time_end, moves_time_start, moves_time_end
    num_evaluations += 1
    eval_time_start += time.time()
    C = 0.1
    total = 0
    for row in range(8):
        for col in range(8):
            piece = piece_at_square(board, row, col)
            moves_time_start += time.time()
            total += MATERIAL[piece] + C*len(get_moves(board, row, col))
            moves_time_end += time.time()
    eval_time_end += time.time()
    return total

def get_all_moves(board, side):
    moves = []
    for row in range(8):
        for col in range(8):
            if get_side(piece_at_square(board, row, col)) == side:
                for move in get_moves(board, row, col):
                    moves.append(((row, col), move))
    return moves

def order_moves_naive(board, side):
    '''Given a board and a side, naively orders the set of all possible moves based solely on whether or not they involve the capture of a piece, and if so, how much the piece is worth.'''
    moves = get_all_moves(board, side)
    moves_and_values = [(move, evaluate(make_move(board, move[0], move[1]))) for move in moves]
    moves_and_values.sort(reverse=(side==1), key=lambda x: x[1])
    return [tup[0] for tup in moves_and_values]

def order_moves_alpha_beta(board, side):
    ### XXX UNUSED FOR NOW
    '''Given a board and a side, orders the set of all possible moves by calling alpha-beta on each move with maximum depth 1.'''
    moves = order_moves_naive(board, side)
    move_and_value_list = []
    for move in moves:
        board = make_move(board, move[0], move[1])
        moveAndValueList.append((move, alpha_beta(board, move, MAX_DEPTH - 1, -1e309, 1e309, -side)))
            
    sorted_move_and_value_list = sorted(move_and_value_list, key = lambda x: x[1], reverse = (side == 1)) #if these moves are being sorted for white, he/she wants the highest ranked move first
    return [move_and_value[0] for move in sorted_move_and_value_list]

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
        best_move = (None, -1000)
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
        best_move = (None, 1000)
        for move in ordered_moves:
            # if depth == 0 and move == ((3, 3), (4, 3)):
            #     breakpoint()
            new_board = make_move(board, move[0], move[1])
            _, move_value = alpha_beta(new_board, depth+1, alpha, beta, 1)
            if move_value < best_move[1]:
                best_move = (move, move_value)
            beta = min(beta, best_move[1])
            if alpha >= best_move[1]:
                return best_move
        return best_move

def make_AI_move(board, side):
    move = alpha_beta(board, 0, -1e309, 1e309, side)[0]
    print(num_evaluations)
    print(eval_time_end - eval_time_start)
    print(moves_time_end - moves_time_start)
    return make_move(board, move[0], move[1])

def draw_board(board, surface):
    ''' Draws all pieces on a given board'''
    # Draw board
    board_img = pygame.transform.scale(BOARD_IMG,(int(800*BOARD_SCALE),int(800*BOARD_SCALE)))
    rect = pygame.Rect(0, 0, surface.get_width(), surface.get_width())
    surface.blit(board_img, rect)

    # Draw pieces
    for row in range(8):
        for col in range(8):
            piece = piece_at_square(board, row, col)
            if not piece:
                continue
            piece_img = PIECE_IMGS[piece]
            # XXX XXX XXX XXX X X X X oh god
            # TODO what sick man sends babies to fight
            width = height = int(50*BOARD_SCALE)
            rect = pygame.Rect(col*100*BOARD_SCALE + (50 - width/2)*BOARD_SCALE, row*100*BOARD_SCALE  + (50 - height/2)*BOARD_SCALE, col*100*BOARD_SCALE + (50 + width/2)*BOARD_SCALE, row*100*BOARD_SCALE + (50 + height/2)*BOARD_SCALE)
            surface.blit(piece_img, rect)

def print_board(board):
    ''' For debugging: just prints all pieces on the board in numeric form'''
    for row in range(8):
        for col in range(8):
            print(piece_at_square(board, row, col), end=' ')
        print()

def highlight_square(surface, row, col):
    global BOARD_SCALE
    highlight_image = pygame.transform.scale(HIGHLIGHT_IMG, (int(100*BOARD_SCALE), int(100*BOARD_SCALE)))
    rect = pygame.Rect((col*100*BOARD_SCALE,row*100*BOARD_SCALE),(100*BOARD_SCALE,100*BOARD_SCALE))
    surface.blit(highlight_image, rect)

def main(two_player, player_side):
    ''' Play chess '''
    global BOARD_SCALE, MAX_DEPTH
    board_image = pygame.image.load("images/chessboard.jpg")
    pygame.init()

    # XXX unused interactive argument setting   
    # valid_scale = False
    # valid_depth = False
    # valid_side = False
    # while valid_scale == False:
    #     BOARD_SCALE = input("Enter the scaling factor for the board (1 corresponds to 800x800):")
    #     try:
    #         BOARD_SCALE = float(BOARD_SCALE)
    #     except:
    #         print("Please enter a positive number less than or equal to 10 as the scaling factor.")
    #         continue
    #     if 0 < BOARD_SCALE and BOARD_SCALE <= 10:
    #         valid_scale = True
    #     else:
    #         print("Please enter a positive number less than or equal to 10 as the scaling factor.")
    #         continue

    # if not two_player:
    #     while valid_depth == False:
    #         depth = input("What depth should the AI search to? 2 is recommended - 3 is more advanced but can take multiple minutes to think.")
    #         try:
    #             MAX_DEPTH = int(depth)
    #         except:
    #             print("Please choose an integer greater than or equal to 0 for the AI's depth.")
    #             continue
    #         if MAX_DEPTH >= 0:
    #             valid_depth = True
    #         else:
    #             print("Please choose an integer greater than or equal to 0 for the AI's depth.")
    #             continue
                
    #     while valid_side == False:
    #         side_string = input("Which side would you like to play as? Please enter \"white\" or \"black\".")
    #         if side_string == 'white' or side_string == 'White':
    #             valid_side = True
    #             player_side = 1
    #         elif side_string == 'black' or side_string == 'Black':
    #             valid_side = True
    #             player_side = -1
    #         elif side_string == "\"white\" or \"black\"":
    #             print("Very funny.")
    #             continue
    #         else:
    #             print("Please enter a valid side (white or black).")
    #             continue
    # else:
    #     player_side = 1
    
    pygame.init()
    width = int(800*BOARD_SCALE)
    height = int(800*BOARD_SCALE)
    surface = pygame.display.set_mode([width, height])
    board_image = pygame.transform.scale(board_image,(width,height))
    board = set_board(variant=VARIANT)
        
    surface.fill([0, 0, 0])
    draw_board(board, surface)
    pygame.display.flip()
        
    first_click = True
    checkmate_value = 0
        
    if two_player:
        player_side = 1
    elif player_side == -1:
        board = make_AI_move(board, -player_side)
        surface.fill([0, 0, 0])
        draw_board(board, surface)
        pygame.display.flip()
    done = False
    while True:
        click_position = [0, 0]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not done: #i.e. when the game is over, the only thing the players can do is exit
                click_position[0] = event.pos[0]
                click_position[1] = event.pos[1]
                click_square = (click_position[1]//int(100*BOARD_SCALE), click_position[0]//int(100*BOARD_SCALE))
                piece = piece_at_square(board, *click_square)
                if first_click:
                    if piece != None and get_side(piece) == player_side:
                        moves = get_moves(board, *click_square)
                        #highlight available moves
                        for move in moves:
                            highlight_square(surface, *move)
                            pygame.display.flip()
                        first_click_square = click_square
                        first_click = False
                        continue #restart the event code, this time getting the move-determining (or selection-cancelling) click
                        
                if not first_click:
                    draw_board(board, surface)
                    pygame.display.flip()
                    if click_square in moves:
                        board = make_move(board, first_click_square, click_square)
                        surface.fill([0, 0, 0])
                        draw_board(board, surface)
                        pygame.display.flip()

                        if player_side == 1:
                            if has_no_moves(board, -1):
                                if test_check(board, -1):
                                    print('White wins!')
                                else:
                                    print('Stalemate.')
                                done = True
                        else:
                            if has_no_moves(board, 1):
                                if test_check(board, 1):
                                    print('Black wins!')
                                else:
                                    print('Stalemate.')
                                done = True
                        # elif checkmate_val == 2:
                        #     print('The game is a draw by stalemate.')
                        # Switch players
                        if not done:
                            if two_player:
                                player_side *= -1
                            else:
                                # cProfile.run('make_AI_move(board, -player_side)')
                                board = make_AI_move(board, -player_side)
                                draw_board(board, surface)
                                pygame.display.flip()

                            # Check to see if the AI checkmated the player
                            if player_side == -1:
                                if has_no_moves(board, -1):
                                    if test_check(board, -1):
                                        print('White wins!')
                                    else:
                                        print('Stalemate.')
                                    done = True
                            else:
                                if has_no_moves(board, 1):
                                    if test_check(board, 1):
                                        print('Black wins!')
                                    else:
                                        print('Stalemate.')
                                    done = True

                    first_click = True
                    
                    
def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--variant', type=str, default='normal',
                        help='type of chess to play')
    parser.add_argument('--two-player', action='store_true', default=False,
                        help='play human vs human')
    parser.add_argument('--depth', type=int, default=2,
                        help='max AI search depth')
    parser.add_argument('--scale', type=int, default=1,
                        help='scaling factor for the board')
    parser.add_argument('--player-side', type=str, default='white',
                        help='side to play vs AI (white or black)')
    args = parser.parse_args()

    if args.player_side == 'white':
        args.player_side = 1
    else:
        args.player_side = -1

    return args

if __name__ == "__main__":
    if len(sys.argv) > 1:
        global BOARD_SCALE, MAX_DEPTH, VARIANT
        args = parse_args()
        BOARD_SCALE = args.scale
        MAX_DEPTH = args.depth
        VARIANT = args.variant
        main(args.two_player, args.player_side)
    else:
        print("Interactive arguments not implemented yet; please set args")
    # while True:
    #     num_players = input("How many players are playing?(1 or 2)")
    #     try:
    #         num_players = int(num_players)
    #     except:
    #         print("Please choose a valid answer - 1 to play against an AI or 2 to play against another human.")
    #         continue
    #     if num_players == 1 or num_players == 2:
    #         main(num_players == 2)
    #     else:
    #         print("Please choose a valid answer - 1 to play against an AI or 2 to play against another human.")

