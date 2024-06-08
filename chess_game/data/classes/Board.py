import pygame

from data.classes.Square import Square
from data.classes.pieces.Rook import Rook
from data.classes.pieces.Bishop import Bishop
from data.classes.pieces.Knight import Knight
from data.classes.pieces.Queen import Queen
from data.classes.pieces.King import King
from data.classes.pieces.Pawn import Pawn

from data.classes.Piece import *

class Board:

	whites = []
	blacks = []

	def __init__(self, width, height, ai = False, depth = 2, log = False):
		self.board = [[]]
		self.width = width
		self.height = height
		self.square_width = width // 8
		self.square_height = height // 8
		self.ai = ai
		self.log = log
		self.selected_piece = None
		self.turn = 'white'

		self.config = [
			['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
			['b ', 'b ', 'b ', 'b ', 'b ', 'b ', 'b ', 'b '],
			['','','','','','','',''],
			['','','','','','','',''],
			['','','','','','','',''],
			['','','','','','','',''],
			['w ', 'w ', 'w ', 'w ', 'w ', 'w ', 'w ', 'w '],
			['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
		]

		self.squares = self.generate_squares()

		self.setup_board()

	def generate_squares(self):
		output = []
		for y in range(8):
			for x in range(8):
				output.append(
					Square(
						x,
						y,
						self.square_width,
						self.square_height
					)
				)

		return output


	def setup_board(self):
		for y, row in enumerate(self.config):
			for x, piece in enumerate(row):
				if piece != '':
					square = self.get_square_from_pos((x, y)) #reference this

					if piece[1] == 'R':
						square.occupying_piece = Rook(
							(x, y),
							'white' if piece[0] == 'w' else 'black',
							self
						)

					elif piece[1] == 'N':
						square.occupying_piece = Knight(
							(x, y),
							'white' if piece[0] == 'w' else 'black',
							self
						)

					elif piece[1] == 'B':
						square.occupying_piece = Bishop(
							(x, y),
							'white' if piece[0] == 'w' else 'black',
							self
						)

					elif piece[1] == 'Q':
						square.occupying_piece = Queen(
							(x, y),
							'white' if piece[0] == 'w' else 'black',
							self
						)

					elif piece[1] == 'K':
						square.occupying_piece = King(
							(x, y),
							'white' if piece[0] == 'w' else 'black',
							self
						)

					elif piece[1] == ' ':
						square.occupying_piece = Pawn(
							(x, y),
							'white' if piece[0] == 'w' else 'black',
							self
						)

		self.save_pieces()

	
	# keep a record of the pieces
	def save_pieces(self):
		for i in range(8):
			for j in range(8):
				if isinstance(self[i][j], Piece):
					if self[i][j].color == 'white':
						self.whites.append(self[i][j])
					else:
						self.blacks.append(self[i][j])

	# move a chess piece on the board
	def move_piece(self, piece, x, y, keep_history = False):
		past_x = piece.x
		past_y = piece.y

		if keep_history == True:
			self.board[past_x][past_y].set_last_eaten_piece(self.board[x][y])

		else: 
			if isinstance(self.board[x][y], Piece):
				if self.board[x][y].color == 'white':
					self.whites.remove(self.board[x][y])
				else:
					self.blacks.remove(self.board[x][y])

		self.board[x][y] = self.board[past_x][past_y]
		self.board[past_x][past_y] = ''
		self.board[x][y].set_position(x, y, keep_history)

	def unmake_move(self, piece):
		x = piece.pos[0]
		y = piece.pos[1]
		self.board[x][y].set_past_position()
		old_x = piece.x
		old_y = piece.y
		self.board[old_x][old_y] = self.board[x][y]
		self.board[x][y] = piece.get_last_eaten_piece()


	def __getitem__(self, item):
		return self.board[item]
	
	def has_opponent(self, piece, x, y):
		if not self.is_valid_move(x, y):
			return False
		if isinstance(self.board[x][y], Piece):
			return piece.color != self[x][y].color
		return False

	# check if piece is a friend
	def has_friend(self, piece, x, y):
		if not self.is_valid_move(x, y):
			return False
		if isinstance(self.board[x][y], Piece): #Square.occupy_piece
			return piece.color == Square.occupy_piece.color
		return False
	
	#checks if is a valid move
	def is_valid_move(x, y):
		return 0 <= x < 8 and 0 <= y < 8
	
	def has_empty_block(self, x, y):
		if not self.is_valid_move(x, y):
			return False
		return not isinstance(self[x][y], Piece)

	def handle_click(self, mx, my):
		x = mx // self.square_width
		y = my // self.square_height
		clicked_square = self.get_square_from_pos((x, y)) #gets the current position of the piece

		if self.selected_piece is None:
			if clicked_square.occupying_piece is not None:
				if clicked_square.occupying_piece.color == self.turn:
					self.selected_piece = clicked_square.occupying_piece #if piece selected is color of player, can play that piece

		#move piece at selected area
		elif self.selected_piece.move(self, clicked_square):
			self.turn = 'white' if self.turn == 'black' else 'black'

		#confirming its your piece lol?
		elif clicked_square.occupying_piece is not None:
			if clicked_square.occupying_piece.color == self.turn:
				self.selected_piece = clicked_square.occupying_piece


	def is_in_check(self, color, board_change=None): # board_change = [(x1, y1), (x2, y2)]
		output = False
		king_pos = None

		changing_piece = None
		old_square = None
		new_square = None
		new_square_old_piece = None

		if board_change is not None:
			for square in self.squares:
				if square.pos == board_change[0]:
					changing_piece = square.occupying_piece
					old_square = square
					old_square.occupying_piece = None
			for square in self.squares:
				if square.pos == board_change[1]:
					new_square = square
					new_square_old_piece = new_square.occupying_piece
					new_square.occupying_piece = changing_piece

		pieces = [
			i.occupying_piece for i in self.squares if i.occupying_piece is not None
		]

		if changing_piece is not None:
			if changing_piece.notation == 'K':
				king_pos = new_square.pos
		if king_pos == None:
			for piece in pieces:
				if piece.notation == 'K':
					if piece.color == color:
						king_pos = piece.pos
		for piece in pieces:
			if piece.color != color:
				for square in piece.attacking_squares(self):
					if square.pos == king_pos:
						output = True

		if board_change is not None:
			old_square.occupying_piece = changing_piece
			new_square.occupying_piece = new_square_old_piece
						
		return output


	def is_in_checkmate(self, color):
		output = False

		for piece in [i.occupying_piece for i in self.squares]:
			if piece != None:
				if piece.notation == 'K' and piece.color == color:
					king = piece

		if king.get_valid_moves(self) == []:
			if self.is_in_check(color):
				output = True

		return output


	def get_square_from_pos(self, pos):
		for square in self.squares:
			if (square.x, square.y) == (pos[0], pos[1]):
				return square


	def get_piece_from_pos(self, pos):
		return self.get_square_from_pos(pos).occupying_piece


	def draw(self, display):
		if self.selected_piece is not None:
			self.get_square_from_pos(self.selected_piece.pos).highlight = True
			for square in self.selected_piece.get_valid_moves(self):
				square.highlight = True

		for square in self.squares:
			square.draw(display)

	# get optimal piece, to implement minimax : 
<<<<<<< Updated upstream
	def get_moves(self, best_move):
		pass 

	
	def optimal_piece(self): #? s
=======
	#def get_moves(self, best_move):
		#self.selected_piece = optimal_piece()

		 
	#def optimal_piece(self, mx, my): #? s
>>>>>>> Stashed changes
		#find the optimal piece and assign it to selected_piece 
		#pass
		#return mx, my


	def get_player_color(self):
		if self.turn == 'white':
			return 'white'
		return 'black'
	
	def king_is_threatened(self, color, move=None):
		output = False

		for piece in [i.occupying_piece for i in self.squares]:
			if piece != None:
				if piece.notation == 'K' and piece.color == color:
					king = piece

		if king.get_valid_moves(self) == []:
			if self.is_in_check(color):
				output = True

		#return output

		output = False

		# Finds the king piece
		for piece in [i.occupying_piece for i in self.squares]:
			if piece != None:
				if piece.notation == 'K' and piece.color == color:
					king = piece

		# checks the color of king and finds its enemies
		if king.color == 'white':
			enemies = self.blacks
		else:
			enemies = self.whites

		#create a list of threats
		threats = []
		for enemy in enemies:
			moves = enemy.get_valid_moves(self)
			if king.pos in moves:
				threats.append(enemy)
		if move and len(threats) == 1 and threats[0] == move:
			output = False
		 
		if len(threats) > 0:
			output = True 
		else: output = False

		return output

		
		#threats = []
		#for enemy in enemies:
			#moves = enemy.get_moves(self)
			#if (king.x, king.y) in moves:
				#threats.append(enemy)
		#if move and len(threats) == 1 and threats[0].x == move[0] and threats[0].y == move[1]:
			#return False
		#return True if len(threats) > 0 else False
	
	def is_terminal(self):
		terminal1 = self.white_won()
		terminal2 = self.black_won()
		terminal3 = self.draw()
		return terminal1 or terminal2 or terminal3
	

	def white_won(self):
		if self.king_is_threatened('black') and not self.has_moves('black'):
			return True
		return False
	
	def black_won(self):
		if self.king_is_threatened('white') and not self.has_moves('white'):
			return True
		return False
	
	def has_moves(self, color):
		total_moves = 0
		for i in range(8):
			for j in range(8):
				if isinstance(self[i][j], Piece) and self[i][j].color == color:
					piece = self[i][j]
					total_moves += len(piece.filter_moves(piece.get_moves(self), self))
					if total_moves > 0:
						return True
		return False
	
	def insufficient_material(self):
		total_white_knights = 0
		total_black_knights = 0
		total_white_bishops = 0
		total_black_bishops = 0
		total_other_white_pieces = 0
		total_other_black_pieces = 0

		for piece in self.whites:
			if piece.type == 'Knight':
				total_white_knights += 1
			elif piece.type == 'Bishop':
				total_white_bishops += 1
			elif piece.type != 'King':
				total_other_white_pieces += 1

		for piece in self.blacks:
			if piece.type == 'Knight':
				total_black_knights += 1
			elif piece.type == 'Bishop':
				total_black_bishops += 1
			elif piece.type != 'King':
				total_other_black_pieces += 1

		weak_white_pieces = total_white_bishops + total_white_knights
		weak_black_pieces = total_black_bishops + total_black_knights

		if self.piece.King.color == 'white' and self.piece.King.color == 'black':
			if weak_white_pieces + total_other_white_pieces + weak_black_pieces + total_other_black_pieces == 0:
				return True
			if weak_white_pieces + total_other_white_pieces == 0:
				if weak_black_pieces == 1:
					return True
			if weak_black_pieces + total_other_black_pieces == 0:
				if weak_white_pieces == 1:
					return True
			if len(self.whites) == 1 and len(self.blacks) == 16 or len(self.blacks) == 1 and len(self.whites) == 16:
				return True
			if total_white_knights == weak_white_pieces + total_other_white_pieces and len(self.blacks) == 1:
				return True
			if total_black_knights == weak_black_pieces + total_other_black_pieces and len(self.whites) == 1:
				return True
			if weak_white_pieces == weak_black_pieces == 1 and total_other_white_pieces == total_other_black_pieces == 0:
				return True


	def evaluate(self):
		white_points = 0
		black_points = 0
		for i in range(8):
			for j in range(8):
				if isinstance(self[i][j], Piece):
					piece = self[i][j]
					if piece.color == 'white':
						white_points += piece.get_score()
					else:
						black_points += piece.get_score()
		if self.game_mode == 0:
			return black_points - white_points
		return white_points - black_points

	def get_king(self, piece):
		if piece.color == 'white':
			return piece.King
		return piece.King

