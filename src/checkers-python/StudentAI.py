from random import randint
from BoardClasses import Move
from BoardClasses import Board
import math
import random
from copy import deepcopy
from time import time
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
EXPLORATION_CONSTANT = 1.414
class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2
        self.root = None
        self.moves_done = 0

    def get_move(self,move):
        self.moves_done += 1
        if len(move) != 0:
            # print("enters because other player already went but game board needs to be updated for this player")
            self.board.make_move(move,self.opponent[self.color])
            if self.root is None:
                # initialize the "root" with the initial state BEFORE OUR AI'S FIRST TURN
                temp_board = deepcopy(self.board)
                self.root = TreeNode(temp_board, self.color, None)
            else:
                # need to go down the tree to the node that corresponds to the move that the other player made
                # and then set that node to be the root
                self.root = self.root.children[str(move)]
                if self.root is None:
                    temp_board = deepcopy(self.board)
                    self.root = TreeNode(temp_board, self.color, None)
        else:
            # print("enters ONLY for first turn of game which means the color of this player is 1 / black")
            self.color = 1
            # initialize the "root" with the initial state BEFORE OUR AI'S FIRST TURN
            temp_board = deepcopy(self.board)
            self.root = TreeNode(temp_board, self.color, None)

        move = self.select_from_mcts()
        self.root = self.root.children[str(move)]       # move the root to the node that corresponds to the best move
        self.board.make_move(move, self.color)          # make the move on the actual board
        return move

    def score(self, temp_color, temp_board):
        # Value of Kings = 300
        # Value of regulars = 100
        # Value of distance from king = (rows - curr_row / rows) * 100
        # Value of center = (- (curr_col - middle_col)^2 + middle_col^2) * 10
        # Value of # of checkers = (Amount of pieces left) / (self.col * self.p / 2) * 10
        # score of current board:
        # Assume self.color is 1 / black, then the score is...
        # Black's (king count * 5 + regular count) - White's (king count * 5 + regular count)
        # self.color explanation:
        # 1 = "B" and 2 = "W"
        white_score = 0
        black_score = 0

        # white_score += self.board.white_count
        # black_score += self.board.black_count
        # this may take too long so maybe do the code above that is commented out
        for row in range(self.row):
            for col in range(self.col):
                checker = temp_board.board[row][col]
                if checker.color == 'W':
                    if checker.is_king:
                        white_score += 300
                    else:
                        white_score += 100
                elif checker.color == 'B':
                    if checker.is_king:
                        black_score += 300
                    else:
                        black_score += 100

        white_score += (temp_board.white_count / (self.col * self.p / 2)) * 10
        black_score += (temp_board.black_count / (self.col * self.p / 2)) * 10

        if temp_color == 1:
            return black_score - white_score
        else:
            return white_score - black_score

    def select_from_mcts(self):
        # for i in range(250):
        for i in range(self.moves_done * 9):
            after_selection = self.selection()
            after_expansion = self.expansion(after_selection)
            self.simulate(after_expansion)
        best_move = self.best_move()
        return best_move

    def selection(self):
        '''Select nodes until it reaches a terminal node and return it or ...'''
        current_node = self.root
        while True:
            # If it is a leaf node, return the node
            if len(current_node.children) == 0:
                return current_node
            # Find the best child with the highest UCT value
            best_child = None
            highest_uct = 0
            for move_str in current_node.children:
                if current_node.children[move_str] is None:
                    return current_node
                elif best_child is None or current_node.children[move_str].uct_val >= highest_uct:
                    best_child = current_node.children[move_str]
                    highest_uct = current_node.children[move_str].uct_val
            # Add the best child to the stack for further exploration
            current_node = best_child

    def expansion(self, node):
        '''expand one node from node given'''
        # If game is not ongoing, just return node
        if node.board.is_win(self.opponent[node.color]) != 0:
            return node
        # expand node when we fild the child is None
        for move_str, child in node.children.items():
            move = Move.from_str(move_str)
            if child is None:   # will always be a child that is None and if not, selection return leaf nodes with no children
                temp_board = deepcopy(node.board)
                temp_board.make_move(move, node.color)
                node.children[move_str] = TreeNode(temp_board, self.opponent[node.color], node)
                return node.children[move_str]

    def simulate(self, node):
        # Do simulation
        simulation_count = 0
        # win: 0 = ongoing, 1 = black, 2 = white, -1 = tie
        win = node.board.is_win(self.opponent[node.color])
        temp_board = deepcopy(node.board)
        temp_color = node.color
        # Iterate until there is winner or 500 times maximum
        while simulation_count < 500 and win == 0:
            temp_board.make_move(self.get_random_move(temp_color, temp_board), temp_color)
            win = temp_board.is_win(temp_color)
            # come back to this (the line below this may need to be at the top of the loop)
            temp_color = self.opponent[temp_color]
            simulation_count += 1

        if win == self.opponent[node.color]:
            win_for_parent = 1
        elif win == node.color:
            win_for_parent = -1
        elif win == -1:     # tie
            win_for_parent = 0  # win for neither
        else:
            if self.score(node.color, temp_board) > 0:
                win_for_parent = -1
            else:
                win_for_parent = 1
        # start backpropagation from the node we simulated from
        node.backpropagation(win_for_parent)

    def get_random_move(self, temp_color, temp_board):
        '''Get random move for simulation and return it'''
        possible_moves = temp_board.get_all_possible_moves(temp_color)
        i = randint(0, len(possible_moves)-1)
        j = randint(0, len(possible_moves[i])-1)
        return possible_moves[i][j]

    def best_move(self):
        '''find best move according to the highest win rate of children which is calculated by wi / si'''
        best_move_str = None
        highest_win_rate = None
        for move_str, child in self.root.children.items():
            if child is not None and (highest_win_rate is None or child.wi / child.si > highest_win_rate):
                best_move_str = move_str
                highest_win_rate = child.wi / child.si
        return Move.from_str(best_move_str)

class TreeNode:
    def __init__(self, board, color, parent):
        # Assuming the board and player color that get passed in
        # are already consistent (i.e. we shouldn't have to modify board on init)
        self.board = board
        self.color = color
        self.parent = parent
        self.opponent = {1: 2, 2: 1}
        self.si = 0 # doesn't get visited until backpropagation
        self.wi = 0
        self.uct_val = 0
        self.children = self._initialize_children()

    def _initialize_children(self):
        # returns a dictionary where the key is the move string and the value is the node
        # initialize the children to be None
        possible_moves = self.board.get_all_possible_moves(self.color)
        children = {}
        for i in range(len(possible_moves)):
            for j in range(len(possible_moves[i])):
                children[str(possible_moves[i][j])] = None
        return children

    def backpropagation(self, win_for_parent):
        # recursively update Si and Wi for this node and parent
        # winForParent = 1 is win for parent, -1 is lose
        self.si += 1
        # if it has parent
        if self.parent is not None:
            self.parent.backpropagation(-win_for_parent)
            if win_for_parent == 1:
                self.wi += 1
            elif win_for_parent == -1:
                self.wi -= 1    # doing this because the mcts tic tac toe demonstrations subtracts on losses
            self.uct_val = self.uct_formula(self.wi, self.si, self.parent.si)

    def uct_formula(self, wi, si, sp):
        return (wi / si) + EXPLORATION_CONSTANT * math.sqrt(math.log(sp) / si)

