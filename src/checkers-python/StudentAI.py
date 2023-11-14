from random import randint
from BoardClasses import Move
from BoardClasses import Board
import math
import random
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
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
    def get_move(self,move):
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1
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

    def min_max(self, depth, max_depth):
        # print("Entered min max function")
        _, move_tuple = self.max_value(depth, max_depth)
        # print("Returning move_tuple:", move_tuple)
        return move_tuple

    def max_value(self, depth, max_depth):
        # print(depth, "Max value function")
        if self.board.is_win("W") != 0 or depth == max_depth:
            # game is over
            score = self.score()
            # print(depth, "Entered if game over:", score)
            return score, None   # maybe multiply wins by 10
        else:
            # print(depth, "Entered else")
            best_value = -float("inf")
            best_move = None
            all_possible_values_from_here = self.board.get_all_possible_moves(self.color)
            for i in range(len(all_possible_values_from_here)):
                for j in range(len(all_possible_values_from_here[i])):
                    # do the move
                    # print(depth, "going to do move", all_possible_values_from_here[i][j])
                    self.board.make_move(all_possible_values_from_here[i][j], self.color)
                    value, _ = self.min_value(depth+1, max_depth)
                    # then undo the move
                    self.board.undo()
                    # print(depth, "undid the move", all_possible_values_from_here[i][j])
                    if value > best_value:
                        best_value = value
                        best_move = all_possible_values_from_here[i][j]
            # print(depth, "Returning max value", best_value, best_move)
            return best_value, best_move

    def min_value(self, depth, max_depth):
        # print(depth, "Min value function")
        if self.board.is_win("W") != 0 or depth == max_depth:
            # game is over
            score = self.score()
            # print(depth, "Entered if game over / exceeded max depth w/ score:", score)
            return score, None  # maybe multiply wins by 10
        else:
            # print(depth, "Entered else")
            best_value = float("inf")
            best_move = None
            all_possible_values_from_here = self.board.get_all_possible_moves(self.opponent[self.color])
            for i in range(len(all_possible_values_from_here)):
                for j in range(len(all_possible_values_from_here[i])):
                    # do the move
                    # print(depth, "going to do move", all_possible_values_from_here[i][j])
                    self.board.make_move(all_possible_values_from_here[i][j], self.opponent[self.color])
                    value, _ = self.max_value(depth + 1, max_depth)
                    # then undo the move
                    self.board.undo()
                    # print(depth, "undid the move", all_possible_values_from_here[i][j])
                    if value < best_value:
                        best_value = value
                        best_move = all_possible_values_from_here[i][j]
            # print(depth, "Returning min value", best_value, best_move)
            return best_value, best_move

    def score(self):
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
                checker = self.board.board[row][col]
                if checker.color == 'W':
                    white_score += 10 * ((self.col/2)**2 -(col - self.col/2)**2)
                    if checker.is_king:
                        white_score += 300
                    else:
                        white_score += 100
                        white_score += ((self.row - row) / self.row) * 100
                elif checker.color == 'B':
                    black_score += 10 * ((self.col/2)**2 -(col - self.col/2)**2)
                    if checker.is_king:
                        black_score += 300
                    else:
                        black_score += 100
                        black_score += (row / self.row) * 100

        white_score += (self.board.white_count / (self.col * self.p / 2)) * 10
        black_score += (self.board.black_count / (self.col * self.p / 2)) * 10

        if self.color == 1:
            return black_score - white_score
        else:
            return white_score - black_score

    def select_from_mcts(self):
        NUMBER_OF_SIMULATIONS = 1000
        # we need from each call to c returned the win or loss (score based)
        # and also this funtion will keep track of
        # the number of simulations from each child node
        all_possible_moves = self.board.get_all_possible_moves(self.color)
        if len(all_possible_moves) == 1:
            # print("Only had one move so don't simulate")
            return all_possible_moves[0][0]
        # all_possible_simulations is a 2d array with variable length rows and i want to
        # initialize a 2 new 2d arrays with the same dimensions with
        # 1. all zeroes to track of the number of simulations from each child node
        # 2. with the average score of each child node
        all_child_counts = []
        all_child_score = []    # this will hold all the totals and then later on we will divide by the counts
        for i in range(len(all_possible_moves)):
            all_child_counts.append([])
            all_child_score.append([])
            for j in range(len(all_possible_moves[i])):
                all_child_counts[i].append(0)
                all_child_score[i].append(0)
        for i in range(NUMBER_OF_SIMULATIONS):
            simulate_start_move = self.rollout_policy()
            # print(i)
            # print(all_child_counts)
            # print(all_child_score)
            all_child_counts[simulate_start_move[0]][simulate_start_move[1]] += 1
            # execute the move
            self.board.make_move(all_possible_moves[simulate_start_move[0]][simulate_start_move[1]], self.color)
            # then simulate the rest of the game
            # and get the score of the game
            all_child_score[simulate_start_move[0]][simulate_start_move[1]] += self.simulate(depth=1, max_depth=5) # since technically this was depth 0
            self.board.undo()
        # now we have all the scores and counts of each child node
        for i in range(len(all_child_score)):
            for j in range(len(all_child_score[i])):
                if all_child_counts[i][j] != 0:
                    all_child_score[i][j] = all_child_score[i][j] / all_child_counts[i][j]
        # now we need to calculate the utc's for these base child nodes
        # and return the best move
        best_move = None
        best_utc = -float("inf")
        for i in range(len(all_child_score)):
            for j in range(len(all_child_score[i])):
                if all_child_counts[i][j] != 0:
                    utc = self.uct_formula(all_child_score[i][j], all_child_counts[i][j], NUMBER_OF_SIMULATIONS)
                    if utc > best_utc:
                        best_utc = utc
                        best_move = [i, j]
        return all_possible_moves[best_move[0]][best_move[1]]

    def simulate(self, depth, max_depth):
        # print(depth, "Simulate function")
        if self.board.is_win("W") != 0 or depth == max_depth:
            # game is over
            score = self.score()
            # print(depth, "Entered if game over:", score)
            return score
        else:
            # print(depth, "Entered else")
            all_possible_values_from_here = self.board.get_all_possible_moves(self.color)
            i, j = self.rollout_policy()
            # print(depth, "going to do move", all_possible_values_from_here[random_row_array_i][random_move_j])
            self.board.make_move(all_possible_values_from_here[i][j], self.color)
            average_value_after = self.simulate(depth+1, max_depth)
            # then undo the move
            self.board.undo()
            # print(depth, "undid the move", all_possible_values_from_here[random_row_array_i][random_move_j])
            return average_value_after

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
        # else:
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
    def uct_formula(self,
                    average_score,
                    child_number_of_simulations,
                    parent_number_of_simulations):
        EXPLORATION_CONSTANT = 1.414
        if child_number_of_simulations == 0:
            return -float("inf")
        return ((average_score / child_number_of_simulations) + (EXPLORATION_CONSTANT * math.sqrt(math.log(parent_number_of_simulations) / child_number_of_simulations)))
