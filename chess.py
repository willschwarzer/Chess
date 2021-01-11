'''
Authors: Blake Johnson and Will Schwarzer
Date of creation: November 10, 2019 (edited by Will Schwarzer afterwards)
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

# 0 represents empty squares
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
# Values chosen to ensure squares divide into board evenly enough
BOARD_SIZE = 614
BOARD_MARGIN = 19
SQUARE_SIZE = 72
# Used for highlighting
last_move = None
# Board scale declared in __main__

def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--alternate-sides', action="store_true", default=False,
                        help='alternate sides (color) every other game')
    parser.add_argument('--display', action="store_true", default=False,
                        help='whether AI games display with the board')
    parser.add_argument('--heuristic-simulation', type=str, nargs='+', default=['False'],
                        help='whether or not to use heuristic to guide random rollouts')
    parser.add_argument('--heuristic-selection', type=str, nargs='+', default=['False'],
                        help='whether or not to use heuristic to guide node selection in rollouts')
    parser.add_argument('--input-file', type=str, nargs='+', default=[],
                        help='which (pickle) file to read in the AI from')
    parser.add_argument('--mcts-depth', type=int, nargs='+', default=[2],
                        help='MCTS max simulation depth (0 for unlimited)')
    parser.add_argument('--mcts-rollouts', type=int, nargs='+', default=[50],
                        help='number of MCTS rollouts')
    parser.add_argument('--minimax-depth', type=int, nargs='+', default=[3],
                        help='minimax max AI search depth')
    parser.add_argument('--num-games', type=int, default=1,
                        help='how many games to play')
    parser.add_argument('--output-file', type=str, nargs='+', default=[],
                        help='which (pickle) file to write the AI to')
    parser.add_argument('--players', type=str, nargs='+', default=['human'],
                        help='who the players are (first is white, second is black)')
    parser.add_argument('--scale', type=float, default=1,
                        help='scaling factor for the board')
    parser.add_argument('--ucb-const', type=float, nargs='+', default=[0.5],
                        help='UCB constant for MCTS')
    parser.add_argument('--variant', type=str, default='normal',
                        help='type of chess to play')
    parser.add_argument('--wait-between', action='store_true', default=False,
                        help='whether or not to wait for a click between games')
    args = parser.parse_args()
    # Convert strings to bools for bool args
    # Done this way rather than using store_true in order to duplicate (below)
    args.heuristic_simulation = [False if string == "False" else True for string in args.heuristic_simulation]
    args.heuristic_selection = [False if string == "False" else True for string in args.heuristic_selection]
    # Duplicate individual args
    if len(args.minimax_depth) == 1:
        args.minimax_depth = args.minimax_depth * 2
    if len(args.input_file) == 1:
        args.input_file = args.input_file * 2
    if len(args.heuristic_simulation) == 1:
        args.heuristic_simulation = args.heuristic_simulation * 2
    if len(args.heuristic_selection) == 1:
        args.heuristic_selection = args.heuristic_selection * 2
    if len(args.mcts_rollouts) == 1:
        args.mcts_rollouts = args.mcts_rollouts * 2
    if len(args.mcts_depth) == 1:
        args.mcts_depth = args.mcts_depth * 2
    if len(args.players) == 1:
        args.players = args.players * 2
    if len(args.ucb_const) == 1:
        args.ucb_const = args.ucb_const * 2
    has_humans = any([player == 'human' for player in args.players])
    args.display = args.display or has_humans
    args.wait_between = args.wait_between or has_humans
    # Ensure that the game waits at end of game if humans are playing

    return args

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
            square_size = int(SQUARE_SIZE*BOARD_SCALE)
            board_margin = int(BOARD_MARGIN*BOARD_SCALE)
            piece_img = pygame.transform.scale(PIECE_IMGS[piece], (square_size,)*2)
            x0 = int(board_margin + col*square_size)
            y0 = int(board_margin + row*square_size)
            rect = pygame.Rect(x0, y0, square_size, square_size)
            surface.blit(piece_img, rect)

def highlight_square(surface, row, col, dark=False):
    ''' Highlights player-selected squares (dark = False) or squares 
    corresponding to the last move (dark = True)'''
    square_size = int(SQUARE_SIZE*BOARD_SCALE)
    board_margin = int(BOARD_MARGIN*BOARD_SCALE)
    highlight_image = pygame.transform.scale(HIGHLIGHT_IMG, (int(square_size),)*2)
    if dark:
        highlight_image = pygame.transform.scale(DARK_HIGHLIGHT_IMG, (int(square_size),)*2)
    # Add a corrective factor here since the square/board ratio is slightly off
    x0 = int(board_margin + col*square_size) + int(3*col/8 + 1)
    y0 = int(board_margin + row*square_size) + int(3*row/8 + 1)
    rect = pygame.Rect(x0, y0, square_size, square_size)
    surface.blit(highlight_image, rect)

def wait_for_click():
    ''' Helper function for waiting at the end of games.'''
    click = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                click = True
            elif event.type == pygame.MOUSEBUTTONUP and click:
                return

class Human(agent.Agent):
    ''' Class for human agents. Defined here to make use of graphics-related
    globals (specifically for highlighting squares).'''
    def __init__(self,side, surface):
        ''' side: integer, 1 or -1 for White or Black
            surface: PyGame surface, for highlighting squares'''
        self.side = side
        self.surface = surface

    def get_move(self,chessboard, pos_counts):
        ''' Return the given human's chosen move.
            chessboard: integer corresponding to the current board
            pos_counts: list of chessboards for determining threefold 
        repetition'''
        # Variable for keeping track of whether the human has selected a piece
        first_click = True
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    row = int((event.pos[1]-board_margin)/square_size)
                    col = int((event.pos[0]-board_margin)/square_size)
                    piece = board.piece_at_square(chessboard, row, col)
                    if first_click:
                        if piece != None and board.get_side(piece) == self.side:
                            moves = board.get_moves(chessboard, row, col, False)
                            # Highlight available moves
                            for move in moves:
                                highlight_square(surface, *move)
                                pygame.display.flip()
                            first_click_square = (row, col)
                            first_click = False
                            # Restart the event code, this time getting the 
                            # Move-determining (or selection-cancelling) click
                            continue 

                    if not first_click:
                        # Attempting to make a move
                        # Clear highlights
                        draw_board(chessboard, surface)
                        pygame.display.flip()
                        if (row, col) in moves:
                            return (first_click_square, (row, col))
                        else:
                            first_click = True

def play_game(agent1, agent2, surface, variant, wait_between):
    ''' Plays one single chess game.
        agent1, agent2: Agents
        surface: PyGame surface
        variant: string indicating the variant (currently either 'normal',
    'horde', or a debug variant
        wait_between: bool indicating whether to wait for click at game end'''
    global last_move # Used for highlighting
    chessboard = board.set_board(variant=variant)
    pos_counts = defaultdict(int)
    if surface:
        surface.fill([0, 0, 0])
        draw_board(chessboard, surface)
        pygame.display.flip()
    # Start a new threefold repetition counter
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
        pos_counts[chessboard] += 1
        # See if White's move caused either checkmate or a draw
        # Note that this function also prints the result
        result = board.get_result(chessboard, pos_counts, variant, 1)
        if result is not None:
            if wait_between:
                print("Click to continue...")
                wait_for_click()
            return result

        move = agent2.get_move(chessboard, pos_counts)
        last_move = move
        if move is None:
            breakpoint()
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


def main(args):
    ''' Runs one or more chess games using some combination of agents.'''
    agents = [None, None]
    for player_no, player in enumerate(args.players):
        side = 1 if player_no == 0 else -1
        if player == "human":
            agents[player_no] = Human(side, surface)
        elif player == "minimax":
            agents[player_no] = Minimax(side, 
                                        args.minimax_depth[player_no], 
                                        args.variant)
        elif player == "mcts":
            input_file = args.input_file[player_no] if args.input_file else None
            output_file = args.output_file[player_no] if args.output_file else None
            # MCTS always starts as White because it records moves
            agents[player_no] = MCTS(1, 
                                     args.mcts_depth[player_no], 
                                     args.mcts_rollouts[player_no],
                                     args.variant, 
                                     args.heuristic_simulation[player_no], 
                                     args.heuristic_selection[player_no],
                                     input_file,
                                     output_file,
                                     args.ucb_const[player_no])

    for i in range(args.num_games):
        play_game(*agents, surface, args.variant, args.wait_between)
        # Reset both MCTS agents to White, since they need to record moves
        if type(agents[0]) == MCTS:
            agents[0].reset(1)
        if type(agents[1]) == MCTS:
            agents[1].reset(1)
        if args.alternate_sides:
            agents[0].switch_sides()
            agents[1].switch_sides()
            temp = agent[0]
            agent[0] = agent[1]
            agent[1] = temp
        # Store the roots of the MCTS trees if output location was specified
        if type(agents[0]) == MCTS:
            agents[0].store_root()
        if type(agents[1]) == MCTS:
            agents[1].store_root()



if __name__ == "__main__":
    args = parse_args()
    BOARD_SCALE = args.scale

    if args.display:
        board_image = pygame.image.load("images/chessboard3.png")
        pygame.init()

        board_size = int(BOARD_SIZE*BOARD_SCALE)
        board_margin = int(BOARD_MARGIN*BOARD_SCALE)
        square_size = int(SQUARE_SIZE*BOARD_SCALE)
        surface = pygame.display.set_mode([board_size]*2)
    else:
        surface = None

    main(args)
