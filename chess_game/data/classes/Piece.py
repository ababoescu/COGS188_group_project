import pygame

class Piece:

	pieces_eaten_history = []
	has_moved_history = []
	position_history = []

	def __init__(self, pos, color, board):
		self.pos = pos
		self.x = pos[0]
		self.y = pos[1]
		self.color = color
		self.has_moved = False

	def move(self, board, square, force=False):

		for i in board.squares:
			i.highlight = False

		if square in self.get_valid_moves(board) or force:
			prev_square = board.get_square_from_pos(self.pos)
			self.pos, self.x, self.y = square.pos, square.x, square.y

			prev_square.occupying_piece = None
			square.occupying_piece = self
			board.selected_piece = None
			self.has_moved = True

			# Pawn promotion
			if self.notation == ' ':
				if self.y == 0 or self.y == 7:
					from data.classes.pieces.Queen import Queen
					square.occupying_piece = Queen(
						(self.x, self.y),
						self.color,
						board
					)

			# Move rook if king castles
			if self.notation == 'K':
				if prev_square.x - self.x == 2:
					rook = board.get_piece_from_pos((0, self.y))
					rook.move(board, board.get_square_from_pos((3, self.y)), force=True)
				elif prev_square.x - self.x == -2:
					rook = board.get_piece_from_pos((7, self.y))
					rook.move(board, board.get_square_from_pos((5, self.y)), force=True)

			return True
		else:
			board.selected_piece = None
			return False


	def get_moves(self, board):
		output = []
		for direction in self.get_possible_moves(board):
			for square in direction:
				if square.occupying_piece is not None:
					if square.occupying_piece.color == self.color:
						break
					else:
						output.append(square)
						break
				else:
					output.append(square)

		return output


	def get_valid_moves(self, board):
		output = []
		for square in self.get_moves(board):
			if not board.is_in_check(self.color, board_change=[self.pos, square.pos]):
				output.append(square)

		return output


	# True for all pieces except pawn
	def attacking_squares(self, board):
		return self.get_moves(board)
	
	# get the last eaten piece
	def get_last_eaten_piece(self):
		return self.pieces_eaten_history.pop()
	
	# add the last eaten piece to array
	def set_last_eaten_piece(self, piece):
		self.pieces_eaten_history.append(piece)


	# update history of piece's position
	def set_position(self, x, y, keep_history):
		if keep_history:
			self.position_history.append(self.x)
			self.position_history.append(self.y)
			self.has_moved_history.append(self.has_moved)
		self.x = x
		self.y = y
		self.has_moved = True

	def set_past_position(self):
		pos_y = self.position_history.pop()
		pos_x = self.position_history.pop()
		self.x = pos_x
		self.y = pos_y
		self.has_moved = self.has_moved_history.pop()

	
	# get the score of the piece
	def get_score(self):
		return 0
	


		