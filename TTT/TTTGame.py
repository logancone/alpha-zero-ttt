from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from .TTTLogic import Board
import numpy as np

class TTTGame(Game):
    square_content = {
        -9: "/", #Unplayable
        -1: "O", #Base Blue
        +0: "-", #Empty
        +1: "X", #Base Red
        +9: "/" #Unplayable
    }

    shop_costs = {
        # Tile Num, Cost
        2: 10, #Double Tile
        3: 50, #Small Bomb Tile
        4: 20 #Shield Tile
    }

    redPoints = 0 #Team 1
    bluePoints = 0 # Team -1

    justBoughtTile = 0
    recentDoubleMove = ()

    @staticmethod
    def getSquarePiece(piece):
        return TTTGame.square_content[piece]

    def __init__(self, n=6,s=3):
        self.n = n
        self.s = s

    def getInitBoard(self):
        # return initial board (numpy board)
        self.s = 3
        self.redPoints = 100
        self.bluePoints = 100
        # for key in self.redInv.keys():
        #     self.redInv[key] = 0
        # for key in self.blueInv.keys():
        #     self.blueInv[key] = 0

        b = Board(self.n, self.s)
        return np.array(b.pieces)

    def getBoardSize(self):
        # (a,b) tuple
        return (self.n, self.n)

    def getActionSize(self):
        # return number of actions
        return self.n*self.n + 1 + len(self.shop_costs)

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        b = Board(self.n, self.s)
        b.pieces = np.copy(board)
        
        # Pass Action
        if action == self.n**2:
            self.redPoints += b.calculate_points(1)
            self.bluePoints += b.calculate_points(-1)

            print(f"Red Points: {self.redPoints}")
            print(f"Blue Points: {self.bluePoints}")
        
            self.s += 1
            b2 = Board(self.n, self.s)
            return (b2.pieces, player)

        # Buy in Shop
        if action > self.n **2:
            tile = -action + self.n ** 2 + 5    
            self.buyTile(tile, player)
            return (b.pieces, player)

        move = (int(action/self.n), action%self.n)

        # Check if Normal Move or Special Move
        if self.justBoughtTile == 0:
            # Normal Move
            b.execute_move(move, player)
        else:
            # Special Move
            match self.justBoughtTile:
                case 2: #Double
                    b.execute_move(move, player) 
                    self.recentDoubleMove = move  
                    self.justBoughtTile = 0
                    return (b.pieces, player)              
                case 3: #Small Bomb
                    b.execute_move(move, player)
                    for y in range(3):
                        for x in range(3):
                            # Ensures the value is between 0 and self.s and then checks if it's 0
                            if move[0] - 1 + x < self.s and move[1] - 1 + y < self.s and move[0] - 1 + x >= 0 and move[1] - 1 + y >= 0 and abs(b.pieces[move[0] - 1 + x][move[1] - 1 + y]) != 4:
                               b.execute_move((move[0] - 1 + x, move[1] - 1 + y), player)
                case 4: #Sheild
                    b.execute_move(move, player * 4)

            self.justBoughtTile = 0
            

        # End of game point calculation
        if self.s == self.n and not b.has_legal_moves():
            self.redPoints += b.calculate_points(1)
            self.bluePoints += b.calculate_points(-1)

            print(f"Red Points: {self.redPoints}")
            print(f"Blue Points: {self.bluePoints}")

            return (b.pieces, player)

        self.recentDoubleMove = ()
        return (b.pieces, -player)

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        valids = [0]*self.getActionSize()
        b = Board(self.n, self.s)
        b.pieces = np.copy(board)

        if self.recentDoubleMove == ():
            legalMoves =  b.get_legal_moves()
        else:
            legalMoves = b.get_legal_moves_after_double(self.recentDoubleMove)
            

        if len(legalMoves)==0:
            # Normal time when no options
            if self.recentDoubleMove == ():
                valids[self.n**2]=1
            else:
                # If its a double with no options
                valids[self.recentDoubleMove[0] * self.n + self.recentDoubleMove[1]] = 1
        else:
            for x, y in legalMoves:
                valids[self.n*x+y]=1

        if self.justBoughtTile == 0 and self.recentDoubleMove == ():
            affordableItems = self.get_affordable_items(player)
            for i in range(len(affordableItems)):
                valids[-(i+1)] = affordableItems[i]

        return np.array(valids)

    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        if(self.n == self.s):
            b = Board(self.n, self.s)
            b.pieces = np.copy(board)
            if b.has_legal_moves():
                return 0
            if self.redPoints > self.bluePoints:
                return 1
            elif self.bluePoints > self.redPoints:
                return -1
            elif self.redPoints == self.bluePoints:
                return 2
        return 0

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        return player*board

    def getSymmetries(self, board, pi):
        # mirror, rotational
        assert(len(pi) == self.n**2+1)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (self.n, self.n))
        l = []

        for i in range(1, 5):
            for j in [True, False]:
                newB = np.rot90(board, i)
                newPi = np.rot90(pi_board, i)
                if j:
                    newB = np.fliplr(newB)
                    newPi = np.fliplr(newPi)
                l += [(newB, list(newPi.ravel()) + [pi[-1]])]
        return l

    def stringRepresentation(self, board):
        return board.tobytes()

    def stringRepresentationReadable(self, board):
        board_s = "".join(self.square_content[square] for row in board for square in row)
        return board_s

    def get_affordable_items(self, player):
        if player == 1:
            points = self.redPoints
        else:
            points = self.bluePoints
        affordable_items = []
        for cost in self.shop_costs.values():
            if points >= cost:
                affordable_items.append(1)
            else:
                affordable_items.append(0)
        return affordable_items

    def buyTile(self, tile, player):
        print(f"BUYINGGGGGGGGGGGGGGGGGGGGGGg {tile} by {player}")
        if player == 1:
            self.redPoints -= self.shop_costs[tile]
            # self.redInv[tile] += 1
            self.justBoughtTile = tile
        else:
            self.bluePoints -= self.shop_costs[tile]
            # self.blueInv[tile] += 1
            self.justBoughtTile = tile


    @staticmethod
    def display(board):
        n = board.shape[0]

        print("   ", end="")
        for y in range(n):
            print (y,"", end="")
        print("")
        print("  ", end="")
        for _ in range(n):
            print ("-", end="-")
        print("--")
        for y in range(n):
            print(y, "|",end="")    # print the row #
            for x in range(n):
                piece = board[y][x]    # get the piece to print
                if piece == -1: print("O ",end="")
                elif piece == 1: print("X ",end="")
                elif piece == 9 or piece == -9: print("/ ", end="")
                elif piece == 4 or piece == -4: print(f"{int(piece)} ", end="")
                else:
                    if x==n:
                        print("-",end="")
                    else:
                        print("- ",end="")
            print("|")

        print("  ", end="")
        for _ in range(n):
            print ("-", end="-")
        print("--")

