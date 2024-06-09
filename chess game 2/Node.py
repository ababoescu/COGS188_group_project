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
        self.ucb = 0 #U pper confidence bound
    def __lt__(self, other):
        return self.ucb < other.ucb
def ucb1(curr_node):
    ans = curr_node.v+2*(sqrt(log(curr_node.N+e+(10**-6))/(curr_node.n+(10**-10))))
    return ans

def rollout(curr_node):

    if(curr_node.state.is_game_over()):
        board = curr_node.state 
        if (board.result() == '1-0'):
            return (1, curr_node)
        elif(board.result() == '0-1'):
            return (-1, curr_node)
        else:
            return (0.5, curr_node)
        
    all_moves = [curr_node.state.san(i) for i in list(curr_node.state.legal_moves)]

    for i in all_moves:
        tmp_state = chess.Board(curr_node.state.fen())
        tmp_state.push_san(i)
        child = Node()
        child.state = tmp_state
        child.parent = curr_node
        curr_node.children.add(child)
    rnd_state = random.choice(list(curr_node.children))

    return rollout(rnd_state)

def expand(curr_node, white):
    if (len(curr_node.children) == 0):
        return curr_node
    max_ucb = -inf
    if(white):
        idx = -1
        max_ucb = -inf
        sel_child = None
        for i in curr_node.children:
            tmp = ucb1(i)
            if( tmp > max_ucb):
                idx = i
                max_ucb = tmp
                sel_child = i
        return (expand(sel_child, 0))
    else:
        idx = -1
        min_ucb = inf
        sel_child = None
        for i in curr_node.children:
            tmp = ucb1(i)
            if (tmp < min_ucb):
                idx = i
                min_ucb = tmp
                sel_child = i
        return expand(sel_child, 1)
    

def rollback(curr_node, reward):
    curr_node.n += 1
    curr_node.v += reward
    while (curr_node.parent != None):
        curr_node.N += 1
        curr_node = curr_node.parent
    return curr_node

def mcts_pred(curr_node, over, white, iterations=10):
    if(over):
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

    while(iterations > 0):
        if(white):
            idx = -1
            max_ucb = -inf
            sel_child = None
            for i in curr_node.children:
                tmp = ucb1(i)
                if(tmp > max_ucb):
                    idx = i
                    max_ucb = tmp
                    sel_child = i

            ex_child = expand(sel_child, 0)
            reward, state = rollout(ex_child)
            curr_node = rollback(state, reward)
            iterations -= 1
        else:
            idx = -1
            min_ucb = inf
            sel_child = None
            for i in curr_node.children:
                tmp = ucb1(i)
                if(tmp < min_ucb):
                    idx = i
                    min_ucb = tmp
                    sel_child = i

            ex_child = expand(sel_child, 1)
            reward, state = rollout(ex_child)
            curr_node = rollback(state, reward)
            iterations -= 1
        
        if(white):
            max = -inf
            idx = -1
            selected_move = ''
            for i in (curr_node.children):
                tmp = ucb1(i)
                if (tmp > max):
                    max = tmp
                    selected_move = map_state_move[i]
            return selected_move
        else:
            min = inf
            idx = -1
            selected_move = ''
            for i in (curr_node.children):
                tmp = ucb1(i)
                if (tmp < min):
                    min = tmp
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

while((not board.is_game_over())):
    all_moves = [board.san(i) for i in list(board.legal_moves)]
    print('')
    print(board)
    print('')
    root = Node()
    root.state = board
    result = mcts_pred(root, board.is_game_over(), white)

    board.push_san(result)

    pgn.append(result)
    white ^= 1 # allows to switch between 2 different states black and white

    # Save the current board state
    board_states.append(board.copy())
    moves += 1

    all_moves = [board.san(i) for i in list(board.legal_moves)]
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
    #ax.imshow([[1, 0] * 4, [0, 1] * 4] * 4, cmap='viridis', alpha=0.3) # this gives yellow and purple
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            #color = 'w' if piece.color == chess.WHITE else 'b'
            piece_unicode = pieces_unicode[piece.symbol()]
            ax.text(square % 8, 7- square // 8, piece_unicode, fontsize = 36, ha='center', va='center')
            #ax.text(square % 8, 7- square // 8, piece.symbol(), fontsize = 36, ha='center', va='center', color=color)


def update(frame):
    plot_board(board_states[frame], ax)

animation = FuncAnimation(fig, update, frames=len(board_states), repeat=False)
animation.save('chess_game.gif', writer='pillow', fps=1)
plt.close(fig)





