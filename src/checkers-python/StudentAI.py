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
    def get_move(self,move):
        if len(move) != 0:
            # print("enters because other player already went but game board needs to be updated for this player")
            self.board.make_move(move,self.opponent[self.color])
            if self.root is None:
                # initialize the "root" with the initial state BEFORE OUR AI'S FIRST TURN
                temp_board = deepcopy(self.board)
                self.root = TreeNode(temp_board, self.color, None, None)
            else:
                # need to go down the tree to the node that corresponds to the move that the other player made
                # and then set that node to be the root
                # print("list of moves for ENEMY to make:", self.root.board.get_all_possible_moves(self.root.color))
                self.root.board.show_board()
                # print(self.root.children)
                # print("ENEMY when changing root the key is:", move, type(move))
                # issue here is O(n) when looking for a key's value
                self.root = self.root.children[str(move)]
                if self.root is None:
                    # make a new Treenode
                    temp_board = deepcopy(self.board)
                    self.root = TreeNode(temp_board, self.color, None, None)
                # print("ENEMY after changing root the board is:")
                # self.root.board.show_board()
                # for k, v in self.root.children.items():
                #     print("k is", k, type(k), "and our move is", move, type(move))
                #     if k == move:
                #         print("found the key")
                #         self.root = self.root.children[move]
                #         print('done')
                #         # self.root = v
                #         break
                # # self.root = self.root.children[move]
        else:
            # print("enters ONLY for first turn of game which means the color of this player is 1 / black")
            self.color = 1
            # initialize the "root" with the initial state BEFORE OUR AI'S FIRST TURN
            temp_board = deepcopy(self.board)
            self.root = TreeNode(temp_board, self.color, None, None)
        # 2d array of moves
        # moves = self.board.get_all_possible_moves(self.color) # comment this out later
        # for i in range(len(moves)):
        #     for j in range(len(moves[i])):
        #         print("moves[i][j]:", moves[i][j], type(moves[i][j]))
        # moves[first=the checker we decide to move][second=direction it moves]
        # loop through all the elements of this moves array
        # these elements are the direct children nodes
        # print()
        # print("(Before Possible Moves):", moves)
        # print("Our AI's color:", self.color)
        # print("About to execute min_max")
        move = self.select_from_mcts()

        # print("before moving the root but after selecting move:", move)
        # print(self.root.board.show_board())
        # print(self.root.color, self.root.children)
        self.root = self.root.children[str(move)]    # move the root to the node that corresponds to the best move
        # print("AFTER moving the root")
        # print(self.root.board.show_board())
        # print(self.root.color, self.root.children)
        # call a function that selects the best move from all possible moves
        # based on the monte carlo tree search algorithm from this node

        self.board.make_move(move, self.color)
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
        for i in range(1000):
            after_selection = self.selection(self.root)
            # print('after selection:', after_selection)
            after_expansion = self.expansion(after_selection)
            # print('after expansion:', after_expansion)
            self.simulate(after_expansion)
        best_move = self.best_move()
        return best_move

    def selection(self, node):
        '''Select nodes until it reach terminal node and return it or ...'''
        # if it is leaf node, return node
        if len(node.children) == 0:
            return node
        # If we visit all children of node, then select node which has highest uct value
        best_child = None
        highest_uct = 0
        for child in node.children.values():
            if child is None:
                return node
            elif best_child is None or child.uct_val >= highest_uct:
                best_child = child
                highest_uct = child.uct_val
        return self.selection(best_child)

    def expansion(self, node):
        '''expand one node from node given'''
        # If game is not ongoing, just return node
        if node.board.is_win(self.opponent[node.color]) != 0:
            return node

        # if it is leaf node, then set its children as None with corresponding move key
        if len(node.children) == 0:
            # going to make children of movees
            # print(node.color, node.board.show_board())
            # print("expansion possible moves:", node.board.get_all_possible_moves(node.color))
            possible_moves = node.board.get_all_possible_moves(node.color)
            for i in range(len(possible_moves)):
                for j in range(len(possible_moves[i])):
                    node.children[str(possible_moves[i][j])] = None

        # expand one of node
        for move_str, child in node.children.items():
            move = Move.from_str(move_str)
            if child is None:
                temp_board = deepcopy(node.board)
                temp_board.make_move(move, node.color)
                node.children[move_str] = TreeNode(temp_board, self.opponent[node.color], move, node)
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
                # print("counted as win after score function called")
                win_for_parent = -1
            else:
                # print("counted as loss after score function called")
                win_for_parent = 1

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
    def __init__(self, board, color, move, parent):
        # Going to assume that the board that gets passed is correct and a copy
        self.board = board
        self.color = color
        # self.move = move
        self.parent = parent
        self.opponent = {1: 2, 2: 1}
        self.si = 0 # doesn't get visited until backpropagation
        self.wi = 0
        self.uct_val = 0

        # if move is not None:
        #     self.board.make_move(move, self.opponent[self.color])

        # Key is str(move) and value is TreeNode of child
        self.children = dict()  # {move STRINGS: TreeNode}

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

