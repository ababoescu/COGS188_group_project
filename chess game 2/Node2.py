import pygame
import chess
import chess.pgn
import chess.engine
import chess.svg
import random
import time
import heapq
from math import log, sqrt, e, inf
#from gymnasium.wrappers import RecordVideo

# for the gif
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt 
from matplotlib.pyplot import colormaps
import matplotlib.image as mpimg
import os
from PIL import Image
import numpy as np

depth = 0

class Node():
    def __init__(self):
        self.state = chess.Board() # current position of board
        self.children = set() # set of all possible states from legal action from current node
        self.parent = None # parent node of current node
        self.N = 0 # number of times parent node has been visited
        self.n = 0 # number of times current node has been visited
        self.v = 0 # exploitation factor of current node
        self.ucb = 0 # Upper confidence bound
    def __lt__(self, other):
        return self.ucb < other.ucb

def ucb1(curr_node):
    ans = curr_node.v + 2 * (sqrt(log(curr_node.N + e + (10 ** -6))/(curr_node.n + (10 ** -10))))
    return ans

def evaluate_board(board):
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 10,
        chess.KING: 0
    }
    value = 0
    for piece_type in piece_values:
        value += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
        value -= len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]
    return value

def rollout(curr_node, depth_limit=10):
    board = curr_node.state 
    depth = 0
    while not board.is_game_over() and depth < depth_limit:
        legal_moves = list(board.legal_moves)
        move_weights = []
        for move in legal_moves:
            board.push(move)
            move_weights.append(evaluate_board(board))
            board.pop()
        total_weight = sum(move_weights)
        if total_weight == 0:
            move = random.choice(legal_moves)
        else:
            probabilities = [weight / total_weight for weight in move_weights]
            move = random.choices(legal_moves, probabilities)[0]
        board.push(move)
        depth += 1

    if board.is_game_over():
        result = board.result()
        if result == '1-0':
            return 1
        elif result == '0-1':
            return -1
        else:
            return 0
    return evaluate_board(board) / 100

def expand(curr_node, white):
    if len(curr_node.children) == 0:
        return curr_node
    max_ucb = -inf
    if white:
        sel_child = None
        for i in curr_node.children:
            tmp = ucb1(i)
            if tmp > max_ucb:
                max_ucb = tmp
                sel_child = i
        return expand(sel_child, 0)
    else:
        sel_child = None
        min_ucb = inf
        for i in curr_node.children:
            tmp = ucb1(i)
            if tmp < min_ucb:
                min_ucb = tmp
                sel_child = i
        return expand(sel_child, 1)
    
rewards = [] # list that stores rewards

def rollback(curr_node, reward):
    curr_node.n += 1
    curr_node.v += reward
    while curr_node.parent is not None:
        curr_node.N += 1
        curr_node = curr_node.parent
    rewards.append(reward) # Append the reward to the list
    return curr_node

def mcts_pred(curr_node, over, white, iterations=500): #updated iterations from 10 to 100
    if over:
        return -1
    all_moves = [curr_node.state.san(i) for i in list(curr_node.state.legal_moves)]
    map_state_move = dict()

    for i in all_moves:
        tmp_state = chess.Board(curr_node.state.fen())
        tmp_state.push_san(i)
        child = Node()
        child.state = tmp_state
        child.parent = curr_node
        curr_node.children.add(child)
        map_state_move[child] = i

    while iterations > 0:
        if white:
            max_ucb = -inf
            sel_child = None
            for i in curr_node.children:
                tmp = ucb1(i)
                if tmp > max_ucb:
                    max_ucb = tmp
                    sel_child = i

            ex_child = expand(sel_child, 0)
            reward = rollout(ex_child)
            curr_node = rollback(ex_child, reward)
            iterations -= 1
        else:
            min_ucb = inf
            sel_child = None
            for i in curr_node.children:
                tmp = ucb1(i)
                if tmp < min_ucb:
                    min_ucb = tmp
                    sel_child = i

            ex_child = expand(sel_child, 1)
            reward = rollout(ex_child)
            curr_node = rollback(ex_child, reward)
            iterations -= 1
        
        if white:
            max_ucb = -inf
            selected_move = ''
            for i in curr_node.children:
                tmp = ucb1(i)
                if tmp > max_ucb:
                    max_ucb = tmp
                    selected_move = map_state_move[i]
            return selected_move
        else:
            min_ucb = inf
            selected_move = ''
            for i in curr_node.children:
                tmp = ucb1(i)
                if tmp < min_ucb:
                    min_ucb = tmp
                    selected_move = map_state_move[i]
            return selected_move

def getRandomLegalMove(curr_node):
    legal_moves = list(curr_node.state.legal_moves)
    rand = random.randrange(len(legal_moves))
    return board.san(legal_moves[rand])


# Main Function
board = chess.Board()

white = 1
moves = 0
pgn = []
game = chess.pgn.Game()
evalutations = []
sm = 0
cnt = 0

# store each board state as an image
board_states = []
#root = Node()
while not board.is_game_over():
    if white == 1:
        print('It is white turn')
        print('')
        print(board)
        print('')

        root = Node()
        root.state = board
        result = mcts_pred(root, board.is_game_over(), white, iterations=500) # added in iterations = 100

        board.push_san(result)

        pgn.append(result)
        white ^= 1 # allows to switch between 2 different states black and white

        # Save the current board state
        board_states.append(board.copy())
        moves += 1
    else:
        print('It is black turn')
        print('')
        print(board)
        print('')
        root = Node()
        root.state = board
        result = getRandomLegalMove(root)
        board.push_san(result)
        pgn.append(result)
        white ^= 1 
        board_states.append(board.copy())
        moves += 1

board_states.append(board.copy())

print(board)
print(' '.join(pgn))
print()
print(board.result())
game.headers['Result'] = board.result()

# Load unicode 
pieces_unicode = {
    "P": "♙", "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔",
    "p": "♟", "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚" 
}

# Create animation using FuncAnimation (from L6)
fig, ax = plt.subplots()

def plot_board(board, ax):
    ax.clear()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.imshow([[1, 0] * 4, [0, 1] * 4] * 4, cmap='gray', alpha=0.3) # gray and white
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_unicode = pieces_unicode[piece.symbol()]
            ax.text(square % 8, 7 - square // 8, piece_unicode, fontsize=36, ha='center', va='center')

def update(frame):
    plot_board(board_states[frame], ax)

animation = FuncAnimation(fig, update, frames=len(board_states), repeat=False)
animation.save('chess_game_2.gif', writer='pillow', fps=1)
plt.close(fig)

plt.figure(figsize=(10, 6))
plt.plot(rewards, marker='o')
plt.title('Updating Rewards Over the Game')
plt.xlabel('Move Number')
plt.ylabel('Reward')
plt.grid(True)
plt.show()
