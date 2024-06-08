import pygame
import argparse
import sys
import numpy as np
import math
import random
from data.classes.Piece import *

from data.classes.Board import Board


# minimax algorithm
def minimax(board, depth, alpha, beta, is_maximizing_player, save_move, data):
    if depth == 0 or board.is_game_over():
        return board.evaluate()

    if is_maximizing_player:
        max_eval = -math.inf
        for i in range(8):
            for j in range(8):
                if isinstance(board[i][j], Piece) and board[i][j].color != board.get_player_color():
                    piece = board[i][j]
                    moves = piece.filter_moves(piece.get_moves(board), board)
                    for move in moves:
                        board.make_move(piece, move[0], move[1], keep_history = True)
                        evaluation = minimax(board, depth -1, alpha, beta, False, False, data) [1]
                        if save_move:
                            if evaluation >= max_eval:
                                if evaluation > data[1]:
                                    data.clear()
                                    data[1] = evaluation
                                    data[0] = [piece, move, evaluation]
                                elif evaluation == data[1]:
                                    data[0].append([piece, move, evaluation])
                        board.unmake_move(piece)
                        max_eval = max(max_eval, evaluation)
                        alpha = max(alpha, evaluation)
                        if beta <= alpha:
                            break

        return data
        
    else:
        min_eval = math.inf
        for i in range(8):
            for j in range(8):
                if isinstance(board[i][j], Piece) and board[i][j].color == board.get_player_color():
                    piece = board[i][j]
                    moves = piece.get_moves(board)
                    for move in moves:
                        board.move_piece(piece)
                        evaluation = minimax(board, depth -1, alpha, beta, True, False, data) [1]
                        board.unmake_move(piece)
                        min_eval = min(min_eval, evaluation)
                        beta = min(beta, evaluation)
                        if beta <= alpha:
                            break
        return data

        
        
def get_ai_move(board):
    moves = minimax(board, board.depth, -math.inf, math.inf, True, True, [[], 0])
    if len(moves[0]) == 0:
        return False
    best_score = max(moves[0], key = lambda x: x[2]) [2]
    piece_and_move = random.choice([move for move in moves[0] if move[2] == best_score])
    piece = piece_and_move[0]
    move = piece_and_move[1]
    if isinstance(piece, Piece) and len(move) > 0 and isinstance(move, tuple):
        board.make_move(piece, move[0], move[1])
    return True

def get_random_mov(board):
    pieces = []
    moves = []
    for i in range(8):
        for j in range(8):
            if isinstance(board[i][j], Piece) and board[i][j].color != board.get_player_color():
                pieces.append(board[i][j])
        for piece in pieces[:]:
            piece_moves = piece.filter_moves(piece.get_moves(board), board)
            if len(piece_moves) == 0:
                pieces.remove(piece)
            else:
                moves.append(piece_moves)
        if len(pieces) == 0:
            return
        piece = random.choice(pieces)
        move = random.choice(moves[pieces.index(piece)])
        if isinstance(piece, Piece) and len(move) > 0:
             board.make_move(piece, move[0], move[1])

              



#def find_best_move(board, depth, is_maximizing_player):
#    print('enter best move')
#    best_move = None
#    best_value = float('-inf') if is_maximizing_player else float('inf')
#    #figure how to find the piece with the optimal move
#    print('looping through valid moves in board')
#    for move in board.selected_piece.get_valid_moves('maximizing_player' if is_maximizing_player else 'minimizing_player'):
#        new_board = board.make_move(move)
#        board_value = minimax(new_board, depth - 1, float('-inf'), float('inf'), not is_maximizing_player)

#        if is_maximizing_player:
#            if board_value > best_value:
#                best_value = board_value
#                best_move = move
#        else:
#            if board_value < best_value:
#                best_value = board_value
#                best_move = move

#    return best_move



#parser for choosing the game type
parser = argparse.ArgumentParser()
parser.add_argument("game_type", help="Type of game: 'human' or 'ai'", choices=["human", "ai"])
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
    print('I am in the ai!')
    while running:
        #if turn == 'black':
            #print('now we are finding the best move')
            #best_move = find_best_move(board, 3, False)
            #print('best move found!')
            #board.selected_piece.move(best_move)
            #turn = 'white'
        print('about to start the first move')
        print('turn is right not:', turn)
        #print('queue of pygame:', pygame.event.get())

        # Human's turn
        mx, my = pygame.mouse.get_pos() # mouse position on board possibly????
        for event in pygame.event.get():
            print('going through pygame')

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    board.handle_click(mx, my)

            if event.type == pygame.MOUSEBUTTONDOWN and turn == 'white': #player 1's turn (HUMAN)
                print('human player turn')
                if board.handle_click(mx, my): 
                    turn = 'black' #now black piece turn

        if board.is_in_checkmate('black'):
            print('White wins!')
            running = False
        elif board.is_in_checkmate('white'):
            print('Black wins!')
            running = False   

        draw(screen)


        #AIs turn
        #if turn == 'black' and running:
             
            

#while running:
    #if player_turn == 'black':  # Assuming AI is playing as black
        #best_move = find_best_move(board, 3, False)
        #board.make_move(best_move)
        #player_turn = 'white'

    #mx, my = pygame.mouse.get_pos()
    #for event in pygame.event.get():
        #if event.type == pygame.QUIT:
            #running = False
        #elif event.type == pygame.MOUSEBUTTONDOWN:
            #if event.button == 1 and player_turn == 'white':
                #if board.handle_click(mx, my):
                    #player_turn = 'black'

    #if board.is_in_checkmate('black'):
        #print('White wins!')
        #running = False
    #elif board.is_in_checkmate('white'):
        #print('Black wins!')
        #running = False
                

