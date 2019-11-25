'''
Authors: Blake Johnson and Will Schwarzer
Date: November 10, 2019
Plays chess with humans or AIs, using pygame for input and display.
This file mostly handles IO for both display and playing the game
'''

import argparse
from collections import defaultdict
import pygame
import time

import sys


import agent
import board
import heuristic
from mcts import MCTS
from minimax import Minimax

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
DARK_HIGHLIGHT_IMG = pygame.image.load("images/highlight2.png")
BOARD_SIZE = 598
BOARD_MARGIN = 18 # was 15
SQUARE_SIZE = (BOARD_SIZE-2*BOARD_MARGIN)/8.0
last_move = None
# Board scale declared in __main__

def draw_board(chessboard, surface):
    ''' Draws all pieces on a given board'''
    global last_move
    # Draw board
    board_img = pygame.transform.scale(BOARD_IMG,(int(BOARD_SIZE*BOARD_SCALE),int(BOARD_SIZE*BOARD_SCALE)))
    rect = pygame.Rect(0, 0, surface.get_width(), surface.get_width())
    surface.blit(board_img, rect)
    if last_move:
        highlight_square(surface, *last_move[0], True)
        highlight_square(surface, *last_move[1], True)

    # Draw pieces
    for row in range(8):
        for col in range(8):
            piece = board.piece_at_square(chessboard, row, col)
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

def highlight_square(surface, row, col, dark=False):
    square_size = (SQUARE_SIZE*BOARD_SCALE)
    board_margin = (BOARD_MARGIN*BOARD_SCALE)
    highlight_image = pygame.transform.scale(HIGHLIGHT_IMG, (int(square_size),)*2)
    if dark:
        highlight_image = pygame.transform.scale(DARK_HIGHLIGHT_IMG, (int(square_size),)*2)
    x0 = int(board_margin + col*square_size) + int(2*col/8 + 1)
    y0 = int(board_margin + row*square_size) + int(2*col/8 + 1)
    rect = pygame.Rect(x0, y0, square_size, square_size)
    surface.blit(highlight_image, rect)

class Human(agent.Agent):
    def __init__(self,side, surface):
        self.side = side
        self.surface = surface

    def get_move(self,chessboard, pos_counts):
        first_click = True
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # click_x = margin_size + row*square_size
                    # row*square_size = click_x - margin_size
                    # row = (click_x - margin_size)/square_size
                    row = int((event.pos[1]-board_margin)/square_size)
                    col = int((event.pos[0]-board_margin)/square_size)
                    piece = board.piece_at_square(chessboard, row, col)
                    if first_click:
                        if piece != None and board.get_side(piece) == self.side:
                            moves = board.get_moves(chessboard, row, col, False, True)
                            #highlight available moves
                            for move in moves:
                                highlight_square(surface, *move)
                                pygame.display.flip()
                            first_click_square = (row, col)
                            first_click = False
                            continue #restart the event code, this time getting the move-determining (or selection-cancelling) click

                    if not first_click:
                        draw_board(chessboard, surface)
                        pygame.display.flip()
                        if (row, col) in moves:
                            return (first_click_square, (row, col))
                        else:
                            first_click = True

def wait_for_click():
    click = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click = True
            elif event.type == pygame.MOUSEBUTTONUP and click:
                return

def play_game(agent1, agent2, surface, variant, wait_between):
    ''' Play chess '''
    global last_move
    chessboard = board.set_board(variant=variant)
    result = None
    pos_counts = defaultdict(int)
    if surface:
        surface.fill([0, 0, 0])
        draw_board(chessboard, surface)
        pygame.display.flip()
    pos_counts[chessboard] += 1
    while True:
        move = agent1.get_move(chessboard, pos_counts)
        last_move = move
        chessboard = board.make_move(chessboard, *move)
        if type(agent1) == MCTS:
            agent1.record_move(move)
        if type(agent2) == MCTS:
            agent2.record_move(move)
        if surface:
            surface.fill([0, 0, 0])
            draw_board(chessboard, surface)
            pygame.display.flip()
        # checkmate checks, etc
        pos_counts[chessboard] += 1
        result = board.get_result(chessboard, pos_counts, variant, 1)
        if result is not None:
            if wait_between:
                print("Click to continue...")
                wait_for_click()
            return result

        move = agent2.get_move(chessboard, pos_counts)
        last_move = move
        chessboard = board.make_move(chessboard, *move)
        if type(agent1) == MCTS:
            agent1.record_move(move)
        if type(agent2) == MCTS:
            agent2.record_move(move)
        if surface:
            surface.fill([0, 0, 0])
            draw_board(chessboard, surface)
            pygame.display.flip()
        pos_counts[chessboard] += 1
        result = board.get_result(chessboard, pos_counts, variant, -1)
        if result is not None:
            if wait_between:
                print("Click to continue...")
                wait_for_click()
            return result
        if surface:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--alternate-sides', action="store_true", default=False,
                        help='alternate sides (color) every other game')
    parser.add_argument('--cuda', action='store_true', default=False,
                        help='whether or not to use gpu')
    parser.add_argument('--display', action="store_true", default=False,
                        help='whether AI games display with the board')
    parser.add_argument('--heuristic-rollouts', type=bool, nargs='+', default=[False],
                        help='whether or not to use heuristic to guide rollouts')
    parser.add_argument('--input-file', type=str, nargs='+', default=[],
                        help='which (pickle) file to read in the AI from')
    parser.add_argument('--mcts-depth', type=int, nargs='+', default=[20],
                        help='MCTS max AI search depth (0 for unlimited)')
    parser.add_argument('--mcts-rollouts', type=int, nargs='+', default=[50],
                        help='number of MCTS rollouts')
    parser.add_argument('--minimax-depth', type=int, nargs='+', default=[2],
                        help='minimax max AI search depth')
    parser.add_argument('--num-games', type=int, default=1,
                        help='how many games to play')
    parser.add_argument('--output-file', type=str, nargs='+', default=[],
                        help='which (pickle) file to write the AI to')
    parser.add_argument('--player1', type=str, default='human',
                        help='who player 1 is (white)')
    parser.add_argument('--player2', type=str, default='minimax',
                        help='who player 2 is (black)')
    parser.add_argument('--scale', type=float, default=1,
                        help='scaling factor for the board')
    parser.add_argument('--variant', type=str, default='normal',
                        help='type of chess to play')
    parser.add_argument('--wait-between', action='store_true', default=False,
                        help='whether or not to wait for a click between games')
    # parser.add_argument('')
    args = parser.parse_args()
    if len(args.minimax_depth) == 1:
        args.minimax_depth = args.minimax_depth * 2
    if args.player1 == 'human' or args.player2 =='human':
        args.wait_between = True
    if len(args.input_file) == 1:
        args.input_file = args.input_file * 2
    if len(args.heuristic_rollouts) == 1:
        args.heuristic_rollouts = args.heuristic_rollouts * 2
    if len(args.mcts_rollouts) == 1:
        args.mcts_rollouts = args.mcts_rollouts * 2
    if len(args.mcts_depth) == 1:
        args.mcts_depth = args.mcts_depth * 2

    return args

def main(args):
    if args.player1 == "human":
        agent1 = Human(1,surface)
    elif args.player1 == "minimax":
        agent1 = Minimax(1, args.minimax_depth[0], args.variant)
    elif args.player1 == "mcts":
        agent1 = MCTS(1, args.mcts_depth[0], args.mcts_rollouts[0],\
         args.variant, args.heuristic_rollouts[0], \
         args.input_file[0] if args.input_file else None, args.output_file[0] if args.output_file else None)

    if args.player2 == "human":
        agent2 = Human(-1, surface)
    elif args.player2 == "minimax":
        agent2 = Minimax(-1, args.minimax_depth[1], args.variant)
    elif args.player2 == "mcts":
        agent2 = MCTS(-1, args.mcts_depth[1], args.mcts_rollouts[1],\
         args.variant, args.heuristic_rollouts[1], args.input_file[1] if len(args.input_file) == 2 else None,\
          args.output_file[1] if len(args.output_file) == 2 else None)

    for i in range(args.num_games):
        play_game(agent1, agent2, surface, args.variant, args.wait_between)
        if type(agent1) == MCTS:
            agent1.reset(1)
        if type(agent2) == MCTS:
            agent2.reset(-1)
        if args.alternate_sides:
            agent1.switch_sides()
            agent2.switch_sides()
            temp = agent1
            agent1 = agent2
            agent2 = temp
        if type(agent1) == MCTS:
            agent1.store_root()
        if type(agent2) == MCTS:
            agent2.store_root()



if __name__ == "__main__":
    args = parse_args()
    BOARD_SCALE = args.scale
    if args.cuda and torch.cuda.is_available():
        DEVICE = torch.device('cuda')

    if args.display or args.player1=="human" or args.player2=="human":
        board_image = pygame.image.load("images/chessboard.jpg")
        pygame.init()

        board_size = int(BOARD_SIZE*BOARD_SCALE)
        board_margin = int(BOARD_MARGIN*BOARD_SCALE)
        square_size = int(SQUARE_SIZE*BOARD_SCALE)
        surface = pygame.display.set_mode([board_size]*2)
    else:
        surface = None

    main(args)
