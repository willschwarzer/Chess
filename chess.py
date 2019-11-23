'''
Authors: Blake Johnson and Will Schwarzer
Date: November 10, 2019
Plays chess with humans or AIs, using pygame for input and display.
This file mostly handles IO for both display and playing the game
'''

import argparse
import numpy as np
import pygame
import torch
import time
import sys

import board
import agent
import minimax


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
# Board scale declared in __main__

NUM_PIECES = 13
POWERS = np.array([NUM_PIECES**n for n in range(70)])

def draw_board(board, surface):
    ''' Draws all pieces on a given board'''
    # Draw board
    board_img = pygame.transform.scale(BOARD_IMG,(int(BOARD_SIZE*BOARD_SCALE),int(BOARD_SIZE*BOARD_SCALE)))
    rect = pygame.Rect(0, 0, surface.get_width(), surface.get_width())
    surface.blit(board_img, rect)

    # Draw pieces
    for row in range(8):
        for col in range(8):
            piece = board.piece_at_square(board, row, col)
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
            print(board.piece_at_square(board, row, col), end=' ')
        print()

def highlight_square(surface, row, col):
    square_size = int(SQUARE_SIZE*BOARD_SCALE)
    board_margin = int(BOARD_MARGIN*BOARD_SCALE)
    highlight_image = pygame.transform.scale(HIGHLIGHT_IMG, (square_size,)*2)
    x0 = (board_margin + col*square_size)
    y0 = (board_margin + row*square_size)
    rect = pygame.Rect(x0, y0, square_size, square_size)
    surface.blit(highlight_image, rect)



class Human(Agent):
    def __init__(self,side, surface):
        self.side = side
        self.surface = surface

    def get_move(self,board):
        while True:
            first_click = True
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # click_x = margin_size + row*square_size
                    # row*square_size = click_x - margin_size
                    # row = (click_x - margin_size)/square_size
                    row = int((event.pos[1]-board_margin)/square_size)
                    col = int((event.pos[0]-board_margin)/square_size)
                    piece = board.piece_at_square(board, row, col)
                    if first_click:
                        if piece != None and get_side(piece) == player_side:
                            moves = board.get_moves(board, row, col)
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
                            return (first_click_square, (row, col))



def wait_for_click():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                return





def play_game(agent1, agent2, surface, variant):
    ''' Play chess '''
    board = board.set_board(variant=variant)
    surface.fill([0, 0, 0])
    draw_board(board, surface)
    pygame.display.flip()
    while True:
        move = agent1.get_move(board)
        board = board.make_move(board,move*)
        if surface:
            surface.fill([0, 0, 0])
            draw_board(board, surface)
            pygame.display.flip()

        # checkmate checks, etc
        if board.has_no_moves(board, -1):
            if board.test_check(board, -1):
                print('White wins!')
                result = 1
            else:
                print('Stalemate.')
                result = 0
            # wait for human to click?
            if type(agent1) == Human or type(agent2) == Human:
                wait_for_click()
            return result

        move = agent2.get_move(board)
        board = board.make_move(board,move*)
        if surface:
            surface.fill([0, 0, 0])
            draw_board(board, surface)
            pygame.display.flip()
        if board.has_no_moves(board, 1):
            if board.test_check(board, 1) or VARIANT == 'horde':
                print('Black wins!')
                result = -1
            else:
                print('Stalemate.')
                result = 0
            if type(agent1) == Human or type(agent2) == Human:
                wait_for_click()
            return result
                    
                    
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

def main(args):
    if args.display or player1=="human" or player2=="human":
        board_image = pygame.image.load("images/chessboard.jpg")
        pygame.init()

        board_size = int(BOARD_SIZE*BOARD_SCALE)
        board_margin = int(BOARD_MARGIN*BOARD_SCALE)
        square_size = int(SQUARE_SIZE*BOARD_SCALE)
        surface = pygame.display.set_mode([board_size]*2)
    else:
        surface = None

    if player1 == "human":
        agent1 = Human(1,surface)
    elif player1 == "minimax":
        agent1 = minimax.Minimax(1, args.minimax_depth)

    if player2 == "human":
        agent2 = Human(2, surface)
    elif player2 == "minimax":
        agent2 = minimax.Minimax(2, args.minimax_depth)

    for i in range(args.num_games):
        play_game(agent1, agent2, surface, args.variant)


if __name__ == "__main__":
    args = parse_args()
    BOARD_SCALE = args.scale
    MAX_DEPTH = args.depth
    VARIANT = args.variant

    if args.cuda and torch.cuda.is_available():
        DEVICE = torch.device('cuda')

    main(args.two_player, args.player_side)
