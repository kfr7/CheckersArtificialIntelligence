from random import randint
from BoardClasses import Move
from BoardClasses import Board
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
        moves = self.board.get_all_possible_moves(self.color) # comment this out later
        # moves[first=the checker we decide to move][second=direction it moves]
        # loop through all the elements of this moves array
        # these elements are the direct children nodes
        # print()
        # print("(Before Possible Moves):", moves)
        # print("Our AI's color:", self.color)
        # print("About to execute min_max")
        move = self.min_max(depth=0, max_depth=4)
        # print("Exiting min_max with:", move)
        # print()

        # randomly chooses which array
        # index = randint(0,len(moves)-1)
        # randomly chooses index inside array
        # inner_index = randint(0,len(moves[index])-1)
        # choose the move
        # move = moves[index][inner_index]
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
                    value, _ = self.min_value(depth + 1, max_depth)
                    # then undo the move
                    self.board.undo()
                    # print(depth, "undid the move", all_possible_values_from_here[i][j])
                    if value < best_value:
                        best_value = value
                        best_move = all_possible_values_from_here[i][j]
            # print(depth, "Returning min value", best_value, best_move)
            return best_value, best_move

    def score(self):
        # Value of Kings = 5
        # Value of regulars = 1
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
                    if checker.is_king:
                        white_score += 5
                    else:
                        white_score += 1
                elif checker.color == 'B':
                    if checker.is_king:
                        black_score += 5
                    else:
                        black_score += 1
        if self.color == 1:
            return black_score - white_score
        else:
            return white_score - black_score
