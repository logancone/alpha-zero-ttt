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

    # redPoints = 0 #Team 1
    # bluePoints = 0 # Team -1

    # justBoughtTile = 0
    # recentDoubleMove = ()

    @staticmethod
    def getSquarePiece(piece):
        return TTTGame.square_content[piece]

    # def __init__(self, n=6,s=3):
    #     self.n = n
    #     self.s = s

    def __init__(self, n=6):
        self.n = n

    def getInitBoard(self):
        # return initial board (numpy board)
        # self.s = 3
        # self.redPoints = 0
        # self.bluePoints = 0

        # b = Board(self.n, self.s)
        b = Board(self.n, 3)


        return (np.array(b.pieces), b.justBoughtTile, b.recentDoubleMove, b.redPoints, b.bluePoints, b.n, b.s)

    def getBoardSize(self):
        # (a,b) tuple
        return (self.n, self.n)

    def getActionSize(self):
        # return number of actions
        return self.n*self.n + 1 + len(self.shop_costs)

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        pieces, jbt, rdm, rp, bp, n, s = board
        b = Board(n, s)
        b.pieces = np.copy(pieces)
        b.justBoughtTile = jbt
        b.recentDoubleMove = rdm
        b.redPoints = rp
        b.bluePoints = bp

        # print(f"Red: {b.redPoints}")
        # print(f"Blue: {b.bluePoints}")
        
        # Pass Action
        if action == n**2:
            # print(f"PASSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS {s} {n}")
            # print("PASS")

            # print(f"PRE: RP: {b.redPoints} | BP: {b.bluePoints}")
            b.redPoints += b.calculate_points(1)
            b.bluePoints += b.calculate_points(-1)
            # print(f"POST: RP: {b.redPoints} | BP: {b.bluePoints}")
            # print(f"Red Points: {self.redPoints}")
            # print(f"Blue Points: {self.bluePoints}")
        
            # if self.s < 6:
            s += 1
            b2 = Board(n, s)
            # b2.pieces = np.full((self.n,self.n), 9)
            # b2.pieces[:self.s, :self.s] = 0
            # b2.n = self.n
            # b2.s = self.s
            # print(f"B2: {b2.pieces}")
            # return (np.copy(b2.pieces),
            #     int(b.justBoughtTile) if b.justBoughtTile else 0,
            #     tuple(b.recentDoubleMove) if b.recentDoubleMove else ()), player
            return (np.copy(b2.pieces), b2.justBoughtTile, b2.recentDoubleMove, b.redPoints, b.bluePoints, n, s), player

        # Buy in Shop
        if action > n **2:
            # print(f"Red: {self.redPoints}")
            # print(f"Blue: {self.bluePoints}")
            tile = -action + n ** 2 + 5    
            self.buyTile(tile, b, player)
            # return (np.copy(b.pieces),
            #     int(b.justBoughtTile) if b.justBoughtTile else 0,
            #     tuple(b.recentDoubleMove) if b.recentDoubleMove else ()), player
            return (np.copy(b.pieces), b.justBoughtTile, b.recentDoubleMove, b.redPoints, b.bluePoints, n, s), player

        move = (int(action/n), action%n)

        # Check if Normal Move or Special Move
        if b.justBoughtTile == 0:
            # Normal Move
            b.execute_move(move, player)
        else:
            # Special Move
            match b.justBoughtTile:
                case 2: #Double
                    b.execute_move(move, player) 
                    b.recentDoubleMove = move  
                    b.justBoughtTile = 0
                    return ((b.pieces, b.justBoughtTile, b.recentDoubleMove, b.redPoints, b.bluePoints, n, s), player)              
                case 3: #Small Bomb
                    b.execute_move(move, player)
                    for y in range(3):
                        for x in range(3):
                            # Ensures the value is between 0 and self.s and then checks if it's 0
                            if move[0] - 1 + x < s and move[1] - 1 + y < s and move[0] - 1 + x >= 0 and move[1] - 1 + y >= 0 and abs(b.pieces[move[0] - 1 + x][move[1] - 1 + y]) != 4:
                               b.execute_move((move[0] - 1 + x, move[1] - 1 + y), player)
                case 4: #Sheild
                    b.execute_move(move, player * 4)

            b.justBoughtTile = 0
            

        # End of game point calculation
        if s == n and not b.has_legal_moves():
            b.redPoints += b.calculate_points(1)
            b.bluePoints += b.calculate_points(-1)

            # print(f"Red Points: {self.redPoints}")
            # print(f"Blue Points: {self.bluePoints}")

            # return (np.copy(b.pieces),
            #     int(b.justBoughtTile) if b.justBoughtTile else 0,
            #     tuple(b.recentDoubleMove) if b.recentDoubleMove else ()), player
            return (np.copy(b.pieces), b.justBoughtTile, b.recentDoubleMove, b.redPoints, b.bluePoints, n, s), player

        b.recentDoubleMove = ()
        # return (np.copy(b.pieces),
        #     int(b.justBoughtTile) if b.justBoughtTile else 0,
        #     tuple(b.recentDoubleMove) if b.recentDoubleMove else ()), -player
        return (np.copy(b.pieces), b.justBoughtTile, b.recentDoubleMove, b.redPoints, b.bluePoints, n, s), -player

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        valids = [0]*self.getActionSize()
        board_array, jbt, rdm, rp, bp, n, s = board

        b = Board(n, s)
        b.pieces = np.copy(board_array)
        b.justBoughtTile = jbt
        b.recentDoubleMove = rdm
        b.redPoints = rp
        b.bluePoints = bp


        if b.recentDoubleMove == ():
            legalMoves =  b.get_legal_moves()
        else:
            legalMoves = b.get_legal_moves_after_double(b.recentDoubleMove)
            

        if len(legalMoves)==0:
            # Normal time when no options
            if b.recentDoubleMove == ():
                valids[n**2]=1
            else:
                # If its a double with no options
                valids[b.recentDoubleMove[0] * n + b.recentDoubleMove[1]] = 1
        else:
            for x, y in legalMoves:
                valids[n*x+y]=1

        # print(f"JBT: {b.justBoughtTile}")
        # print(f"RDM: {b.recentDoubleMove}")
        if b.justBoughtTile == 0 and b.recentDoubleMove == ():
            affordableItems = self.get_affordable_items(b, player)
            for i in range(len(affordableItems)):
                valids[-(i+1)] = affordableItems[i]

        return np.array(valids)

    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        pieces, jbt, rdm, rp, bp, n, s = board

        if(n == s):
            # print(f"SS: {s}")
            # print(f"SN: {n}")
            
            b = Board(n, s)
            b.pieces = np.copy(pieces)


            # print(f"BS: {b.s}")
            # print(f"BN: {b.n}")
            # print(pieces)
            if b.has_legal_moves():
                return 0
            if rp > bp:
                return 1
            elif bp > rp:
                return -1
            elif rp == bp:
                return 2
        return 0

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        pieces, jbt, rdm, rp, bp, n, s = board
        return (player*pieces, jbt, rdm, rp, bp, n, s)

    def getSymmetries(self, board, pi):
        # Lowkey chatGPTed ts function so rip
        """
        Generate symmetrical versions of the board and policy, but only for
        the active SxS playable region. Unplayable cells and non-board actions
        (pass/shop) remain unchanged.
        """
        board_array, jbt, rdm, rp, bp, n, s = board
        # n = self.n
        # s = self.s  # current playable area size

        

        # Number of actions related to board positions
        board_action_count = n ** 2
        extra_actions = pi[board_action_count:]  # pass + shop actions (unchanged)

        # Split policy into board region + extras
        pi_board = np.reshape(pi[:board_action_count], (n, n))

        # Isolate playable area
        playable_board = board_array[:s, :s]
        playable_pi = pi_board[:s, :s]

        symmetries = []

        for rot in range(4):  # 0°, 90°, 180°, 270°
            for flip in [False, True]:
                # Rotate playable region
                newB = np.rot90(playable_board, rot)
                newPi = np.rot90(playable_pi, rot)

                # Optional horizontal mirror
                if flip:
                    newB = np.fliplr(newB)
                    newPi = np.fliplr(newPi)

                # Embed back into full board shape
                newFullBoard = np.copy(board_array)
                newFullBoard[:s, :s] = newB

                # Rebuild pi with only playable region replaced
                newFullPi = np.zeros_like(pi_board)
                newFullPi[:s, :s] = newPi

                # Flatten board-policy and reattach extra actions
                symmetries.append((newFullBoard, list(newFullPi.ravel()) + list(extra_actions)))

        return symmetries

    def stringRepresentation(self, board):
        pieces, jbt, rdm, rp, bp, n, s = board
        return (pieces.tobytes(), jbt, rdm, rp, bp, n, s)
        # return board[0].tobytes()

    def stringRepresentationReadable(self, board):
        pieces, jbt, rdm, rp, bp, n, s = board
        board_s = "".join(self.square_content[square] for row in pieces for square in row)
        return f"{board_s} | jbt={jbt} | rdm={rdm} | Red Points={rp} | Blue Points={bp} | N={n} |S={s}"

    def get_affordable_items(self, b, player):
        if player == 1:
            points = b.redPoints
        else:
            points = b.bluePoints
        affordable_items = []
        for cost in self.shop_costs.values():
            if points >= cost:
                affordable_items.append(1)
            else:
                affordable_items.append(0)
        return affordable_items

    def buyTile(self, tile, board, player):
        # print(f"BUYINGGGGGGGGGGGGGGGGGGGGGGg {tile} by {player}")
        if player == 1:
            board.redPoints -= self.shop_costs[tile]
            # self.redInv[tile] += 1
            board.justBoughtTile = tile
        else:
            board.bluePoints -= self.shop_costs[tile]
            # self.blueInv[tile] += 1
            board.justBoughtTile = tile


    @staticmethod
    def display(board):
        n = board[0].shape[0]

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
                piece = board[0][y][x]    # get the piece to print
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

