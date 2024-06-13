import pygame

from data.classes.Board import Board
from Node import *

pygame.init() # game is being initialized

# screen and board is being printed
WINDOW_SIZE = (1000, 1000)
screen = pygame.display.set_mode(WINDOW_SIZE)

board = Board(WINDOW_SIZE[0], WINDOW_SIZE[1])

# drawing  the board
def draw(display):
	display.fill('white')

	board.draw(display)

	pygame.display.update()

# While the game is running
running = True
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