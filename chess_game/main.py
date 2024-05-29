import pygame
import argparse
import sys
import numpy as np
import math
import random

from data.classes.Board import Board

#parser for choosing the game type
parser = argparse.ArgumentParser()
parser.add_argument("game_type', help='Type of game: 'human' or 'ai'", choices=["human", "ai"])
args = parser.parse_args()

# Initialize Pygame
pygame.init()

WINDOW_SIZE = (800, 800)
screen = pygame.display.set_mode(WINDOW_SIZE)

board = Board(WINDOW_SIZE[0], WINDOW_SIZE[1])
turn = 'white'

def draw(display):
	display.fill('white')

	board.draw(display)

	pygame.display.update()

#Human vs Human
running = True
if args.game_type == "human":
	while running:
		mx, my = pygame.mouse.get_pos()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					board.handle_click(mx, my)

		if board.is_in_checkmate('black'):
			print('White wins!')
			running = False
		elif board.is_in_checkmate('white'):
			print('Black wins!')
			running = False         

		draw(screen)
     

#Human vs AI
else:
    while running:
        mx, my = pygame.mouse.get_pos() # mouse position on board possibly????
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    board.handle_click(mx, my)
            if event.type == pygame.MOUSEBUTTONDOWN and turn == 0: #player 1's turn (HUMAN)
                board.handle_click(mx, my) 

                
                




# minimax algorithm
def minimax(board, depth, alpha, beta, is_maximizing_player):
    if depth == 0 or board.is_game_over():
        return board.evaluate()

    if is_maximizing_player:
        max_eval = float('-inf')
        for move in board.generate_legal_moves('maximizing_player'):
            new_board = board.make_move(move)
            eval = minimax(new_board, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.generate_legal_moves('minimizing_player'):
            new_board = board.make_move(move)
            eval = minimax(new_board, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(board, depth, is_maximizing_player):
    best_move = None
    best_value = float('-inf') if is_maximizing_player else float('inf')

    for move in board.generate_legal_moves('maximizing_player' if is_maximizing_player else 'minimizing_player'):
        new_board = board.make_move(move)
        board_value = minimax(new_board, depth - 1, float('-inf'), float('inf'), not is_maximizing_player)

        if is_maximizing_player:
            if board_value > best_value:
                best_value = board_value
                best_move = move
        else:
            if board_value < best_value:
                best_value = board_value
                best_move = move

    return best_move
