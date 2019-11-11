import pygame
from enum import Enum
import sys

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

board_scale = 1

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

    # TODO add ep? or maybe just add this is an extra int to the board?

    # def setBoard(self):
    #     '''Given an empty board, initializes a set of pieces for a standard game of chess'''
    #     whitePawnImage = pygame.image.load("images/whitepawn.png")
    #     blackPawnImage = pygame.image.load("images/blackpawn.png")
    #     whiteKnightImage = pygame.image.load("images/whiteknight.png")
    #     blackKnightImage = pygame.image.load("images/blackknight.png")
    #     whiteBishopImage = pygame.image.load("images/whitebishop.png")
    #     blackBishopImage = pygame.image.load("images/blackbishop.png")
    #     whiteRookImage = pygame.image.load("images/whiterook.png")
    #     blackRookImage = pygame.image.load("images/blackrook.png")
    #     whiteQueenImage = pygame.image.load("images/whitequeen.png")
    #     blackQueenImage = pygame.image.load("images/blackqueen.png")
    #     whiteKingImage = pygame.image.load("images/whiteking.png")
    #     blackKingImage = pygame.image.load("images/blackking.png")
        
    #     self.pieceList = []
    #     for col in range(8):
    #         self.boardList[1][col] = Pawn('black', 1, col, self, blackPawnImage, self.surface)
    #         self.boardList[6][col] = Pawn('white', 6, col, self, whitePawnImage, self.surface)
    #     self.boardList[0][1] = Knight('black', 0, 1, self, blackKnightImage, self.surface)
    #     self.boardList[0][6] = Knight('black', 0, 6, self, blackKnightImage, self.surface)
    #     self.boardList[7][1] = Knight('white', 7, 1, self, whiteKnightImage, self.surface)
    #     self.boardList[7][6] = Knight('white', 7, 6, self, whiteKnightImage, self.surface)
    #     self.boardList[0][2] = Bishop('black', 0, 2, self, blackBishopImage, self.surface)
    #     self.boardList[0][5] = Bishop('black', 0, 5, self, blackBishopImage, self.surface)
    #     self.boardList[7][2] = Bishop('white', 7, 2, self, whiteBishopImage, self.surface)
    #     self.boardList[7][5] = Bishop('white', 7, 5, self, whiteBishopImage, self.surface)
    #     self.boardList[0][0] = Rook('black', 0, 0, self, blackRookImage, self.surface)
    #     self.boardList[0][7] = Rook('black', 0, 7, self, blackRookImage, self.surface)
    #     self.boardList[7][0] = Rook('white', 7, 0, self, whiteRookImage, self.surface)
    #     self.boardList[7][7] = Rook('white', 7, 7, self, whiteRookImage, self.surface)
    #     self.boardList[0][3] = Queen('black', 0, 3, self, blackQueenImage, self.surface)
    #     self.boardList[7][3] = Queen('white', 7, 3, self, whiteQueenImage, self.surface)
    #     self.boardList[0][4] = King('black', 0, 4, self, blackKingImage, self.surface)
    #     self.boardList[7][4] = King('white', 7, 4, self, whiteKingImage, self.surface)
        
    #     for row in self.boardList:
    #         for square in row:
    #             if square != None:
    #                 self.pieceList.append(square)

def set_board():
    ''' Represented digitally: each square is a place, counting horizontally
    from the upper left, and each piece is an enum'''
    board = 0
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
    start_square = start[0]*8 + start[1]
    finish_square = finish[0]*8 + finish[1]
    piece = piece_at_square(board, *start)
    diff = piece*(len(Piece)**finish_square) - \
            piece*(len(Piece)**start_square) - \
            piece_at_square(board, *finish)*(len(Piece)**finish_square)
    return board + diff

def find_king(board, side):
    if side == 1:
        king = Piece.white_king.value
    else:
        king = Piece.black_king.value
    for row in range(8):
        for col in range(8):
            if king == piece_at_square(board, row, col):
                return (row, col)
    raise RuntimeException('Unless this is a variant, each side should have a king!')

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

def is_legal(board, start, finish, threatened=False):
    ''' Returns a piece-independent evaluation of whether or not a given
    move is legal. Easily extended to different rulesets, such as antichess.
    If threatened is true, then checks whether or not the given piece
    threatens the square (e.g., this will be true if it has a friend there.)'''
    if not in_bounds(*finish):
        return False
    # If we're just checking threat, we don't care about being in check
    if threatened:
        return True
    side = get_side(piece_at_square(board, *start))
    if get_side(piece_at_square(board, *finish)) == side:
        return False
    # If it results in a check for the player making the move, nope on out
    if test_check(make_move(board, start, finish), side):
        return False
    return True

def get_moves(board, row, col, threatened=False):
    piece = piece_at_square(board, row, col)
    if not piece:
        raise RuntimeException('Got moves for empty square?')
    if piece in (1, 2):
        return get_moves_pawn(board, row, col, threatened)
    if piece in (3, 4):
        return get_moves_knight(board, row, col, threatened)
    if piece in (5, 6):
        return get_moves_bishop(board, row, col, threatened)
    if piece in (7, 8):
        return get_moves_rook(board, row, col, threatened)
    if piece in (9, 10):
        return get_moves_queen(board, row, col, threatened)
    return get_moves_king(board, row, col, threatened)

def get_moves_pawn(board, row, col, threatened=False):
    side = get_side(piece_at_square(board, row, col))
    moves = []
    if side == 1:
        if threatened:
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
        # TODO might be a little slower than doing the logic in the if statement
    else:
        if threatened:
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

    return [move for move in moves if is_legal(board, (row, col), move)]

def get_moves_knight(board, row, col, threatened=False):
    side = get_side(piece_at_square(board, row, col))
    moves = [(row+2, col-1),(row+2, col+1),(row+1,col-2), (row+1,col+2),(row-1,col-2),(row-1,col+2),(row-2,col-1),(row-2, col+1)]
    return [move for move in moves if is_legal(board, (row, col), move, threatened)]

def get_moves_bishop(board, row, col, threatened=False):
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
    return [move for move in moves if is_legal(board, (row, col), move, threatened)]

def get_moves_rook(board, row, col, threatened=False):
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
    return [move for move in moves if is_legal(board, (row, col), move, threatened)]

def get_moves_queen(board, row, col, threatened=False):
    side = get_side(piece_at_square(board, row, col))
    moves = []
    i = 0
    diags = get_moves_bishop(board, row, col, threatened)
    orthogs = get_moves_rook(board, row, col, threatened)
    return diags + orthogs

def get_moves_king(board, row, col, threatened=False):
    side = get_side(piece_at_square(board, row, col))
    moves = [(row, col+1), (row+1,col), (row+1, col+1), (row-1, col),(row,col-1), (row-1, col-1), (row+1, col-1), (row-1, col+1)]
    return [move for move in moves if is_legal(board, (row, col), move, threatened)]

def has_no_moves(board, side):
    for row in range(8):
        for col in range(8):
            if get_side(piece_at_square(board, row, col)) == side:
                if get_moves(board, row, col):
                    return False
    return True

def draw_board(board, surface):
    ''' Draws all pieces on a given board'''
    # Draw board
    board_img = pygame.transform.scale(BOARD_IMG,(int(800*board_scale),int(800*board_scale)))
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
            width = height = int(50*board_scale)
            rect = pygame.Rect(col*100*board_scale + (50 - width/2)*board_scale, row*100*board_scale  + (50 - height/2)*board_scale, col*100*board_scale + (50 + width/2)*board_scale, row*100*board_scale + (50 + height/2)*board_scale)
            surface.blit(piece_img, rect)

def highlight_square(surface, row, col):
    global board_scale
    highlight_image = pygame.transform.scale(HIGHLIGHT_IMG, (int(100*board_scale), int(100*board_scale)))
    rect = pygame.Rect((col*100*board_scale,row*100*board_scale),(100*board_scale,100*board_scale))
    surface.blit(highlight_image, rect)

def two_player():
    '''Method for allowing two humans to play against each other'''
    global board_scale
    board_image = pygame.image.load("images/chessboard.jpg")
    pygame.init()
    
    valid_scale = False
    valid_depth = False
    valid_side = False
    while valid_scale == False:
        board_scale = input("Enter the scaling factor for the board (1 corresponds to 800x800):")
        try:
            board_scale = float(board_scale)
        except:
            print("Please enter a positive number less than or equal to 10 as the scaling factor.")
            continue
        if 0 < board_scale and board_scale <= 10:
            valid_scale = True
        else:
            print("Please enter a positive number less than or equal to 10 as the scaling factor.")
            continue
    
    pygame.init()
    width = int(800*board_scale)
    height = int(800*board_scale)
    surface = pygame.display.set_mode([width, height])
    board_image = pygame.transform.scale(board_image,(width,height))
    board = set_board()
        
    surface.fill([0, 0, 0])
    draw_board(board, surface)
    pygame.display.flip()
        
    player_side = 1
    first_click = True
    checkmate_value = 0
        
    while True:
        click_position = [0, 0]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and checkmate_value == 0: #i.e. when the game is over, the only thing the players can do is exit
                click_position[0] = event.pos[0]
                click_position[1] = event.pos[1]
                click_square = (click_position[1]//int(100*board_scale), click_position[0]//int(100*board_scale))
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
                            if test_check(board, -1) and has_no_moves(board, -1):
                                print('White wins!')
                        else:
                            if test_check(board, 1) and has_no_moves(board, 1):
                                print('Black wins!')
                        # elif checkmate_val == 2:
                        #     print('The game is a draw by stalemate.')
                        # Switch players
                        player_side *= -1
                            
                    first_click = True
                    
                    
def vs_AI():
    '''Launches a game against an AI'''
    global board_scale
    board_image = pygame.image.load("images/chessboard.jpg")
    pygame.init()
    
    valid_scale = False
    valid_depth = False
    valid_side = False
    while valid_scale == False:
        board_scale = input("Enter the scaling factor for the board (1 corresponds to 800x800):")
        try:
            board_scale = float(board_scale)
        except:
            print("Please enter a positive number less than or equal to 10 as the scaling factor.")
            continue
        if 0 < board_scale and board_scale <= 10:
            valid_scale = True
        else:
            print("Please enter a positive number less than or equal to 10 as the scaling factor.")
            continue
            
    while valid_depth == False:
        depth = input("What depth should the AI search to? 2 is recommended - 3 is more advanced but can take multiple minutes to think.")
        try:
            depth = int(depth)
        except:
            print("Please choose an integer greater than or equal to 0 for the AI's depth.")
            continue
        if depth >= 0:
            valid_depth = True
        else:
            print("Please choose an integer greater than or equal to 0 for the AI's depth.")
            continue
            
    while valid_side == False:
        side = input("Which side would you like to play as? Please enter \"white\" or \"black\".")
        if side == 'white' or side == 'White' or side == 'black' or side == 'Black':
            valid_side = True
        elif side == "\"white\" or \"black\"":
            print("Very funny.")
            continue
        else:
            print("Please enter a valid side (white or black).")
            continue
    
    
    width = int(800*board_scale)
    height = int(800*board_scale)
    surface = pygame.display.set_mode([width, height])
    board_image = pygame.transform.scale(board_image, (width, height))

    board = Board(board_image, surface)
    board.set_board()
    
    if side == 'white':
        ai = AI(depth, 'black')
    else:
        ai = AI(depth, 'white')
        
    surface.fill([0, 0, 0])
    board.draw_everything()
    pygame.display.flip()
        
    player_side = side
    first_click = True
    checkmate_value = 0
        
    while True:
        #handle the AI being white by just adding an extra move to the start before the event handling code
        if board.move_counter == 0 and side == 'black':
            board.make_AI_Move(ai)
            board.update_board_list()
            surface.fill([0, 0, 0])
            board.draw_everything()
            pygame.display.flip()
            
        click_position = [0, 0]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and checkmate_value == 0:
                click_position[0] = event.pos[0]
                click_position[1] = event.pos[1]
                click_square = [click_position[1]//int(100*board_scale), click_position[0]//int(100*board_scale)]
                piece = board.board_list[click_square[0]][click_square[1]]
                
                if first_click:
                    if piece != None and piece.get_side() == player_side:
                        moves = board.get_piece_moves(click_square)
                        highlighted_squares = []
                        for move in moves:
                            board.highlight_square(move)
                            highlighted_squares.append(move)
                            pygame.display.flip()
                        first_click_square = click_square
                        first_click = False
                        continue
                        
                if not first_click:
                    for square in highlighted_squares:
                            board.un_highlight_square(square)
                    pygame.display.flip()
                    valid_move = False
                    for move in moves:
                        if move == click_square:
                            valid_move = True        
                    if valid_move:
                        board.make_move(first_click_square, click_square)
                        board.update_board_list()
                        surface.fill([0, 0, 0])
                        board.draw_everything()
                        pygame.display.flip()
                        
                        checkmate_value = board.get_checkmate()
                        if checkmate_value == 1:
                            print('White wins!')
                            continue
                        elif checkmate_value == 2:
                            print('Black wins!')
                            continue
                        elif checkmate_value == 3:
                            print('The game is a draw by stalemate.')
                            continue
                            
                        check_value = board.get_check()
                        if check_value != 0 and checkmate_value == 0:
                            print('Check.')
                            
                        board.make_AI_Move(ai)
                        board.update_board_list()
                        surface.fill([0, 0, 0])
                        board.draw_everything()
                        pygame.display.flip()
                        
                        checkmate_value = board.get_checkmate()
                        if checkmate_value == 1:
                            print('White wins!')
                            continue
                        elif checkmate_value == 2:
                            print('Black wins!')
                            continue
                        elif checkmate_value == 3:
                            print('The game is a draw by stalemate.')
                            
                        check_value = board.get_check()
                        if check_value != 0 and checkmate_value == 0:
                            print('Check.')
                        
                    first_click = True
    

if __name__ == "__main__":
    while True:
        mode = input("How many players are playing?(1 or 2)")
        try:
            mode = int(mode)
        except:
            print("Please choose a valid answer - 1 to play against an AI or 2 to play against another human.")
            continue
        if mode == 1:
            vs_aI()
        elif mode == 2:
            two_player()
        else:
            print("Please choose a valid answer - 1 to play against an AI or 2 to play against another human.")

