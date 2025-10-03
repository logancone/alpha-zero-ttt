'''Board class for TTT
Board will start at 3x3 and grow after each round

Board data:
1 = Red (X), -1 = Blue (O), 0 = Empty
first dim is column, second dim is row
'''
import numpy as np 

class Board():
    
    
    def __init__(self, n, s):
        #  Set up initial board configuration.
        self.n = n
        self.s = s

        # Create the empty board array.
        self.pieces = np.zeros((self.n,self.n))
        
        self.set_board_size()

    # add [][] indexer syntax to the Board
    def __getitem__(self, index): 
        return self.pieces[index]

    def get_legal_moves(self):
        """Returns all the legal moves for the given color.
        (1 for red, -1 for blue
        """
        moves = set()  # stores the legal moves.
        moveList = []
        # Get all the squares with pieces of the given color.
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y]==0:
                    moveList.append((x,y))
        moves.update(moveList)
        return list(moves)

    def has_legal_moves(self):
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y]==0:
                    return True
        return False

    def execute_move(self, move, color):
        """Perform the given move on the board; flips pieces as necessary.
        color gives the color pf the piece to play (1=red,-1=blue)
        """

        self[move[0]][move[1]] = color

    def set_board_size(self):
        for i in range(self.n):
            for j in range(self.n):
                if(i >= self.s or j >= self.s):
                    self.pieces[i][j] = 9

    def calculate_points(self, team):
        tictactoes = 0
        print(f"Team: {team}")  

        for i in range(self.s):
            for j in range(self.s):
                # If two down in still in range
                if ((i + 2) % self.s > i % self.s):
                    if self[i][j] == team and self[i + 1][j] == team and self[i + 2][j] == team:
                        tictactoes += 1
                        print(f"Down vertical at: {i, j}")
                    
                    # If two down and two right is in range
                    if((j + 2) % self.s > j % self.s):
                        if self[i][j] == team and self[i + 1][j + 1] == team and self[i + 2][j + 2] == team:
                            tictactoes += 1
                            print(f"Down right diagonal at: {i, j}")
                
                    # If two down and two left is in range
                    if((j - 2) >= 0 and (j - 2) % self.s < j % self.s):
                        if self[i][j] == team and self[i + 1][j - 1] == team and self[i + 2][j - 2] == team:
                            tictactoes += 1
                            print(f"Down left diagonal at {i, j}")

                # If two left is still in range 
                if ((j + 2) % self.s > j % self.s):
                    if self[i][j] == team and self[i][j + 1] == team and self[i][j + 2] == team:
                        tictactoes += 1
                        print(f"Right horizontal at: {i, j}")

        """"
        for i in range(self.s * self.s):
            if ((i + 2) % self.s > i % self.s):
                if self[i] == team and self[i + 1] == team and self[i + 2] == team:
                    tictactoes += 1
                    print("HOR")

            if (i + (2 * self.s) < self.s * self.s):        
                if (self[i] == team and self[i + self.s] == team and self[i + (2 * self.s)] == team):          
                    tictactoes += 1
                    print("VERT")
                
            if ((i + (2 * (self.s - 1))) % self.s < i % self.s and i + (2 * (self.s - 1)) < self.s * self.s):
                if (self[i] == team and self[i + self.s - 1] == team and self[i + (2 * (self.s - 1))] == team):      
                    tictactoes += 1
                    print("LEFT DIA")

            if ((i + (2 * (self.s + 1))) % self.s > i % self.s and i + (2 * (self.s + 1)) < self.s * self.s):       
                if (self[i] == team and self[i + self.s + 1] == team and self[i + (2 * (self.s + 1))] == team):    
                    tictactoes += 1
                    print("RIGHT DIA")
        """""

        # Count Pieces
        pieces = 0
        for x in range(self.s):
            for y in range(self.s):
                if self.pieces[x][y] == team:
                    pieces += 1

        
        print(f"Number of pieces: {pieces}")
        print(f"Number of tictactoes: {tictactoes}")
        print(f"Total points: {pieces + (tictactoes * 10)}")

        return pieces + (tictactoes * 10)         
    
        
    
        

