import argparse
import cProfile
from enum import Enum
import numpy as np
import pygame
import torch
import time
import sys

PIECE_IMGS = [
    None,
    pygame.image.load("images/whitepawn2.png"),
    pygame.image.load("images/blackpawn2.png"),
    pygame.image.load("images/whiteknight2.png"),
    pygame.image.load("images/blackknight2.png"),
    pygame.image.load("images/whitebishop2.png"),
    pygame.image.load("images/blackbishop2.png"),
    pygame.image.load("images/whiterook2.png"),
    pygame.image.load("images/blackrook2.png"),
    pygame.image.load("images/whitequeen2.png"),
    pygame.image.load("images/blackqueen2.png"),
    pygame.image.load("images/whiteking2.png"),
    pygame.image.load("images/blackking2.png")
]
BOARD_IMG = pygame.image.load("images/chessboard3.png")
HIGHLIGHT_IMG = pygame.image.load("images/highlight.png")
BOARD_SIZE = 598
BOARD_MARGIN = 15
SQUARE_SIZE = (BOARD_SIZE-2*BOARD_MARGIN)/8

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

one_dim_vals = np.array([[0.1, 0.2, 0.3, 1, 1, 0.3, 0.2, 0.1]])
SQUARE_VALS = np.transpose(one_dim_vals) @ one_dim_vals
# SQUARE_VALS = np.array([[0.1]*8]*2 + [[0.1, 0.2, 0.3, 0.7, 0.7, 0.3, 0.2, 0.1]] + [[0.3, 0.4, 0.7, 1, 1, 0.7, 0.4, 0.3]]*2 + [[0.2]*8] + [[0.1]*8]*2)

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

NUM_PIECES = len(MATERIAL)
POWERS = np.array([NUM_PIECES**n for n in range(70)])

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
            board += Piece.black_pawn.value*POWERS[place]
            place = 6*8 + col
            board += Piece.white_pawn.value*POWERS[place]
        # Knights
        for col in (1, 6):
            place = 0*8 + col
            board += Piece.black_knight.value*POWERS[place]
            place = 7*8 + col
            board += Piece.white_knight.value*POWERS[place]
        # Bishops
        for col in (2, 5):
            place = 0*8 + col
            board += Piece.black_bishop.value*POWERS[place]
            place = 7*8 + col
            board += Piece.white_bishop.value*POWERS[place]
        # Rooks
        for col in (0, 7):
            place = 0*8 + col
            board += Piece.black_rook.value*POWERS[place]
            place = 7*8 + col
            board += Piece.white_rook.value*POWERS[place]
        # Queens
        place = 0*8 + 3
        board += Piece.black_queen.value*POWERS[place]
        place = 7*8 + 3
        board += Piece.white_queen.value*POWERS[place]

        # Kings
        place = 0*8 + 4
        board += Piece.black_king.value*POWERS[place]
        place = 7*8 + 4
        board += Piece.white_king.value*POWERS[place]
        # Castling: both sides start at 3, i.e. can castle either side
        board += 3*POWERS[WHITE_CASTLE_DIGIT]
        board += 3*POWERS[BLACK_CASTLE_DIGIT]
    elif variant == 'horde':
        # Pawns
        for col in range(8):
            place = 1*8 + col
            board += Piece.black_pawn.value*POWERS[place]
        # Knights
        for col in (1, 6):
            place = 0*8 + col
            board += Piece.black_knight.value*POWERS[place]
        # Bishops
        for col in (2, 5):
            place = 0*8 + col
            board += Piece.black_bishop.value*POWERS[place]
        # Rooks
        for col in (0, 7):
            place = 0*8 + col
            board += Piece.black_rook.value*POWERS[place]
        # Queens
        place = 0*8 + 3
        board += Piece.black_queen.value*POWERS[place]
        # Kings
        place = 0*8 + 4
        board += Piece.black_king.value*POWERS[place]
        # White pawns
        for row in range(4, 8):
            for col in range(8):
                place = row*8 + col
                board += Piece.white_pawn.value*POWERS[place]
        for col in (1, 2, 5, 6):
            place = 3*8 + col
            board += Piece.white_pawn.value*POWERS[place]
        # Castling: Only black can castle (not that it matters)
        board += 3*POWERS[BLACK_CASTLE_DIGIT]
    elif variant == 'test':
        place = 3*8 + 3
        board += Piece.black_pawn.value*POWERS[place]
        place = 6*8 + 4
        board += Piece.white_pawn.value*POWERS[place]
        place = 0*8 + 3
        board += Piece.black_king.value*POWERS[place]
        place = 7*8 + 4
        board += Piece.white_king.value*POWERS[place]
        # No castling
    # En passant initialized to nonexistent, i.e. row, col = 8, 8
    place = 66
    board += 8*POWERS[EP_ROW_DIGIT]
    place = 67
    board += 8*POWERS[EP_COL_DIGIT]
    # num_insignificant_moves starts at 0, i.e. is 0 / n and 0 % n
    return board

def reset_insignificant_moves(board):
    return board % POWERS[INSIG_MOD_N_DIGIT]

def increment_insignificant_moves(board):
    return board + POWERS[INSIG_MOD_N_DIGIT]

def get_insignificant_moves(board):
    return board // POWERS[INSIG_MOD_N_DIGIT]

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
    # return (board // POWERS[square]) % NUM_PIECES

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
                if get_moves(board, row, col, check_check=True):
                    return False
    return True


def get_all_moves(board, side):
    moves = []
    for row in range(8):
        for col in range(8):
            if get_side(piece_at_square(board, row, col)) == side:
                for move in get_moves(board, row, col):
                    moves.append(((row, col), move))
    return moves



def make_AI_move(board, side, AI_agent):
    #move = alpha_beta(board, 0, -100000, 100000, side)[0]
    move = AI_agent.make_move()
    return make_move(board, move[0], move[1])

def draw_board(board, surface):
    ''' Draws all pieces on a given board'''
    # Draw board
    board_img = pygame.transform.scale(BOARD_IMG,(int(BOARD_SIZE*BOARD_SCALE),int(BOARD_SIZE*BOARD_SCALE)))
    rect = pygame.Rect(0, 0, surface.get_width(), surface.get_width())
    surface.blit(board_img, rect)

    # Draw pieces
    for row in range(8):
        for col in range(8):
            piece = piece_at_square(board, row, col)
            if not piece:
                continue
            # XXX XXX XXX XXX X X X X oh god
            # TODO what sick man sends babies to fight
            square_size = int(SQUARE_SIZE*BOARD_SCALE)
            board_margin = int(BOARD_MARGIN*BOARD_SCALE)
            piece_img = pygame.transform.scale(PIECE_IMGS[piece], (square_size,)*2)
            x0 = int(board_margin + col*square_size)
            y0 = int(board_margin + row*square_size)
            rect = pygame.Rect(x0, y0, square_size, square_size)
            surface.blit(piece_img, rect)

def print_board(board):
    ''' For debugging: just prints all pieces on the board in numeric form'''
    for row in range(8):
        for col in range(8):
            print(piece_at_square(board, row, col), end=' ')
        print()

def highlight_square(surface, row, col):
    square_size = int(SQUARE_SIZE*BOARD_SCALE)
    board_margin = int(BOARD_MARGIN*BOARD_SCALE)
    highlight_image = pygame.transform.scale(HIGHLIGHT_IMG, (square_size,)*2)
    x0 = (board_margin + col*square_size)
    y0 = (board_margin + row*square_size)
    rect = pygame.Rect(x0, y0, square_size, square_size)
    surface.blit(highlight_image, rect)

def play_AI_game(agent1, agent2, does_display=False, num_games=1):

def play_human_game(player_side, AI=None):
    ''' Play chess '''

    global BOARD_SCALE, MAX_DEPTH
    board_image = pygame.image.load("images/chessboard.jpg")
    pygame.init()

    board_size = int(BOARD_SIZE*BOARD_SCALE)
    board_margin = int(BOARD_MARGIN*BOARD_SCALE)
    square_size = int(SQUARE_SIZE*BOARD_SCALE)
    surface = pygame.display.set_mode([board_size]*2)
    board_image = pygame.transform.scale(board_image,(board_size,)*2)
    board = set_board(variant=VARIANT)
        
    surface.fill([0, 0, 0])
    draw_board(board, surface)
    pygame.display.flip()
        
    first_click = True
    checkmate_value = 0
        
    if not AI:
        player_side = 1
    elif player_side == -1:
        board = make_AI_move(board, -player_side)
        surface.fill([0, 0, 0])
        draw_board(board, surface)
        pygame.display.flip()
    done = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not done: #i.e. when the game is over, the only thing the players can do is exit
                # click_x = margin_size + row*square_size
                # row*square_size = click_x - margin_size
                # row = (click_x - margin_size)/square_size
                row = int((event.pos[1]-board_margin)/square_size)
                col = int((event.pos[0]-board_margin)/square_size)
                piece = piece_at_square(board, row, col)
                if first_click:
                    if piece != None and get_side(piece) == player_side:
                        moves = get_moves(board, row, col)
                        #highlight available moves
                        for move in moves:
                            highlight_square(surface, *move)
                            pygame.display.flip()
                        first_click_square = (row, col)
                        first_click = False
                        continue #restart the event code, this time getting the move-determining (or selection-cancelling) click
                        
                if not first_click:
                    draw_board(board, surface)
                    pygame.display.flip()
                    if (row, col) in moves:
                        board = make_move(board, first_click_square, (row, col))
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
                                if test_check(board, 1) or VARIANT == 'horde':
                                    print('Black wins!')
                                else:
                                    print('Stalemate.')
                                done = True
                        # Switch players
                        if not done:
                            if not AI:
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
                                    if test_check(board, 1) or VARIANT=='horde':
                                        print('Black wins!')
                                    else:
                                        print('Stalemate.')
                                    done = True

                    first_click = True
                    
                    
def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--variant', type=str, default='normal',
                        help='type of chess to play')
    parser.add_argument('--player1', type=str, default='human',
                        help='who player 1 is (white)')
    parser.add_argument('--player2', type=str, default='minimax',
                        help='who player 2 is (black)')
    parser.add_argument('--minimax-depth', type=int, default=2,
                        help='minimax max AI search depth')
    parser.add_argument('--scale', type=float, default=1,
                        help='scaling factor for the board')
    parser.add_argument('--alternate-sides', action="store_true", default=False,
                        help='alternate sides (color) every other game')
    
    parser.add_argument('--num-games', type=int, default=1,
                        help='how many games to play')
    parser.add_argument('--display-AI-games', action="store_true", default=False,
                        help='if an AI game displays with the board')
    parser.add_argument('--cuda', action='store_true', default=False,
                        help='whether or not to use gpu')
    # parser.add_argument('')
    args = parser.parse_args()

    # if args.self_play != None:
    #     if len(args.self_play) == 1:
    #         args.self_play = 2*args.self_play
    #     if len(args.self_play != 2):
    #         raise RuntimeError('Please specify exactly two algs for self-play')
    #     for alg in args.self_play:
    #         if alg not in ['minimax', 'mcts']:
    #             raise RuntimeError('Please specify valid algs for self-play')
    #     if args.self_play[0] == 'minimax':
    #         raise RuntimeError('You can\'t train minimax with self-play!')

    #if args.player_side == 'white':
    #    args.player_side = 1
    #else:
    #    args.player_side = -1

    return args

if __name__ == "__main__":
    global BOARD_SCALE, MAX_DEPTH, VARIANT, DEVICE
    args = parse_args()
    BOARD_SCALE = args.scale
    MAX_DEPTH = args.depth
    VARIANT = args.variant
    if args.cuda and torch.cuda.is_available():
        DEVICE = torch.device('cuda')
    # if args.self_play != None:
    #     self_play(args.self_play[0], args.self_play[1], args.num_self_play_games)
    #main(args.two_player, args.player_side)
