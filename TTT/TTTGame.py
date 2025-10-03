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

    redInv = {
        # Tile Num, Count
        2: 0,
        3: 0,
        4: 0
    }
    blueInv = {
        # Tile Num, Count
        2: 0,
        3: 0,
        4: 0
    }

    @staticmethod
    def getSquarePiece(piece):
        return TTTGame.square_content[piece]

    def __init__(self, n=4,s=3):
        self.n = n
        self.s = s

    def getInitBoard(self):
        # return initial board (numpy board)
        self.s = 3
        self.redPoints = 0
        self.bluePoints = 0
        for key in self.redInv.keys():
            self.redInv[key] = 0
        for key in self.blueInv.keys():
            self.blueInv[key] = 0

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
        
        if action == self.n**2:
            self.redPoints += b.calculate_points(1)
            self.bluePoints += b.calculate_points(-1)

            print(f"Red Points: {self.redPoints}")
            print(f"Blue Points: {self.bluePoints}")
        
            self.s += 1
            b2 = Board(self.n, self.s)
            return (b2.pieces, player)

        if action > self.n **2:
            tile = action - self.n ** 2
            self.buyTile(tile, player)

        move = (int(action/self.n), action%self.n)
        b.execute_move(move, player)

        if self.s == self.n and not b.has_legal_moves():
            self.redPoints += b.calculate_points(1)
            self.bluePoints += b.calculate_points(-1)

            print(f"Red Points: {self.redPoints}")
            print(f"Blue Points: {self.bluePoints}")

            # self.s += 1
            # b2 = Board(self.n, self.s)
            return (b.pieces, player)

        return (b.pieces, -player)

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        valids = [0]*self.getActionSize()
        print(valids)
        b = Board(self.n, self.s)
        b.pieces = np.copy(board)
        legalMoves =  b.get_legal_moves()
        affordableItems = self.get_affordable_items(player)

        if len(legalMoves)==0:
            valids[self.n**2]=1
            # return np.array(valids)
        else:
            for x, y in legalMoves:
                valids[self.n*x+y]=1
        
        for i in range(len(affordableItems)):
            valids[-i] = affordableItems[i]
            
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
        for cost in self.shop_costs.items():
            if points >= cost:
                affordable_items.append(1)
            else:
                affordable_items.append(0)
        print(affordable_items)
        return affordable_items

    def buyTile(self, tile, player):
        if player == 1:
            self.redPoints -= self.shop_costs[tile]
            self.redInv[tile] += 1
        else:
            self.bluePoints -= self.shop_costs[tile]
            self.blueInv[tile] += 1


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

