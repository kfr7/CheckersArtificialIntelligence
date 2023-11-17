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
        self.root = TreeNode(self.board, self.color, None, None)
    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
            self.root = TreeNode(self.board, self.color, None, None)
        # 2d array of moves
        # moves = self.board.get_all_possible_moves(self.color) # comment this out later
        # moves[first=the checker we decide to move][second=direction it moves]
        # loop through all the elements of this moves array
        # these elements are the direct children nodes
        # print()
        # print("(Before Possible Moves):", moves)
        # print("Our AI's color:", self.color)
        # print("About to execute min_max")
        move = self.select_from_mcts()

        # call a function that selects the best move from all possible moves
        # based on the monte carlo tree search algorithm from this node

        # make the move on the board
        self.board.make_move(move,self.color)
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
            after_expansion = self.expansion(after_selection)
            self.simulate(after_expansion)
        best_move = self.best_move()
        return best_move

    def selection(self, node):
        '''Select nodes until it reach terminal node and return it or ...'''
        # if it is leaf node, return node
        if len(node.children) == 0:
            return node
        # If we visit all children of node, then select node which has highest utc value
        if None not in node.children.values():
            best_child = None
            highest_utc = 0
            for child in node.children.values():
                if child.UTC_val >= highest_utc:
                    best_child = child
                    highest_utc = child.UTC_val
            return self.selection(best_child)
        # if one of children is not explored
        else:
            return node

    def expansion(self, node):
        '''expand one node from node given'''
        # If game is not ongoing, just return node
        if node.board.is_win(self.opponent[node.color]) != 0:
            return node

        # if it is leaf node, then set its children as None with corresponding move key
        if len(node.children) == 0:
            possible_moves = node.board.get_all_possible_moves(node.color)
            for i in range(len(possible_moves)):
                for j in range(len(possible_moves)):
                    node.children[possible_moves[i][j]] = None

        # expand one of node
        for move, child in node.children.items():
            if child is None:
                node.children[move] = TreeNode(node.board, self.opponent[node.color], move, node)
                return node.children[move]

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
            temp_color = self.opponent[temp_color]
            simulation_count += 1

        if win == self.opponent[node.color]:
            win_for_parent = 1
        elif win == node.color:
            win_for_parent = -1
        else:
            if self.score(node.color, temp_board) > 0:
                win_for_parent = -1
            else:
                win_for_parent = 1

        node.backpropagation(win_for_parent)

    def get_random_move(self, temp_color, temp_board):
        '''Get random move for simulation and return it'''
        possible_moves = temp_board.get_all_possible_moves(temp_color)
        i = randint(0, len(possible_moves)-1)
        j = randint(0, len(possible_moves[i])-1)
        return possible_moves[i][j]

    def best_move(self):
        '''find best move according to highest utc? maybe visit count not sure, might be visit count
        since high utc child will be visited more'''
        best_move = None
        highest_si = 0
        for move, child in self.root.children.items():
            if child.Si > highest_si:
                best_move = move
                highest_si = child.Si
        return best_move

    def rollout_policy(self, epsilon=0.2):
        """
        Picks moves for the rollout phase of MCTS
        (can still be improved because right now uses static "score"
        but might be better if we use the win numbers that we are
        getting from the simulations)
        """
        all_possible_moves = self.board.get_all_possible_moves(self.color)
        # explore: choose a random move
        i = random.randint(0, len(all_possible_moves)-1)
        j = random.randint(0, len(all_possible_moves[i])-1)
        return [i, j]
        # else: # was too biased towards the move with the highest score and treated
        #       # all other moves the same even though some may have been better than others
        #     # exploitation: choose the move with the highest score (just uses board score)
        #     best_move = None
        #     best_score = -float("inf")
        #     for i in range(len(all_possible_moves)):
        #         for j in range(len(all_possible_moves[i])):
        #             self.board.make_move(all_possible_moves[i][j], self.color)
        #             score_for_move = self.score()
        #             if self.score() > best_score:
        #                 best_score = score_for_move
        #                 best_move = [i, j]
        #             self.board.undo()
        #     return best_move


class TreeNode:
    def __init__(self, board, color, move, parent):
        self.board = deepcopy(board)
        self.color = color
        self.move = move
        self.parent = parent
        self.opponent = {1: 2, 2: 1}

        self.Si = 1
        self.Wi = 0
        self.UCT_val = 0

        if move is not None:
            self.board.make_move(move, self.opponent[self.color])

        # Key is move and value is TreeNode of child
        self.children = dict()

    def backpropagation(self, win_for_parent):
        # recursively update Si and Wi for this node and parent
        # winForParent = 1 is win for parent, -1 is lose
        self.Si += 1
        # if it has parent
        if self.parent is not None:
            self.parent.backpropagation(-win_for_parent)

            if win_for_parent == 1:
                self.Wi += 1

            self.UTC_val = self.uct_formula(self.Wi, self.Si, self.parent.Si)

    def uct_formula(self, wi, si, sp):

        return (wi / si) + EXPLORATION_CONSTANT * math.sqrt(math.log(sp) / si)
