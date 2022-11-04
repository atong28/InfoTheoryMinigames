import argparse
import time
import os
import numpy as np

class Battleship():

    def __init__(self, generateRandom, allowAdjacent):
        self.board = Board(generateRandom, allowAdjacent)
        
        while True:
            nextMove = tuple(input("Enter row, col [format: xy, where x:[0,9], y:[0,9]]:"))
            self.board.move(int(nextMove[0]), int(nextMove[1]))

################################################################################
# BOARD CLASS: Stores the game state with both the actual ship allocation and  #
# the guessed state.                                                           #
# ---------------------------------------------------------------------------- #
# CONSTANTS                                                                    #
# - BOARD_SIZE: The size of the allocated board.                               #
# - DEFAULT_SHIP_SIZES: The sizes of the ships available to allocate.          #
# ---------------------------------------------------------------------------- #
# INSTANCE VARIABLES:                                                          #
# - hiddenState:    The array that stores the actual allocation. 0 indicates   #
#                   nothing. 1 indicates a ship exists there.                  #
# - guessState:     The array that stores the guessed allocation. 0 indicates  #
#                   possible/confirmed, 1 indicates missed/not possible.       #
# - gameState:      The same thing as guessState, except 0 for not checked,    #
#                   1 for missed, 2 for hit.                                   #
# - probState:      Higher for more likely spots for ships.                    #
# - ships:          The array that stores Ship objects.                        #
# - generateRandom: True if the array is to be generated at random.            #
# - allowAdjacent:  True if ships are allowed to 'touch'. False if not.        #
################################################################################
class Board():
    BOARD_SIZE = 10
    DEFAULT_SHIP_SIZES = [5,4,3,3,2]
    
    ############################################################################
    # Initializes the board.                                                   #
    ############################################################################
    def __init__(self, generateRandom, allowAdjacent):

        self.generateRandom = generateRandom
        self.allowAdjacent = allowAdjacent

        self.reset()
        if self.generateRandom:
            self.generate()
        else:
            pass #manual generation

        print(self)

    ############################################################################
    # Resets the board state.                                                  #
    # Clears hiddenState, guessState, ships                                    #
    ############################################################################
    def reset(self):
        self.hiddenState = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        self.guessState = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        self.gameState = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        self.ships = []
        self.evalBoard()
        

    ############################################################################
    # Generates an orientation of ships by random. Only used after a reset.    #
    # adjacent: True if ships may touch. False if ships cannot.                #
    ############################################################################
    def generate(self):
        print("Generating a new random board...")
        for shipSize in self.DEFAULT_SHIP_SIZES:

            while True:
                orientation = np.random.randint(2)
                
                if orientation == 0:
                    x = np.random.randint(self.BOARD_SIZE)
                    y = np.random.randint(self.BOARD_SIZE - shipSize + 1)
                else:
                    x = np.random.randint(self.BOARD_SIZE - shipSize + 1)
                    y = np.random.randint(self.BOARD_SIZE)

                if not self.overlaps(x, y, orientation, shipSize, self.hiddenState, self.allowAdjacent):
                    if orientation == 0:
                        self.hiddenState[x,y:y+shipSize] = 1
                    else:
                        self.hiddenState[x:x+shipSize,y] = 1
                    break
            self.ships.append(Ship(shipSize, x, y, orientation))
            print("Created: "+str(self.ships[-1]))

    ############################################################################
    # Prints the board state.                                                  #
    ############################################################################
    def __str__(self):
        string = '''HIDDEN BOARD            GUESS BOARD'''
        for row in range(self.BOARD_SIZE):
            string += "\n"+str(self.hiddenState[row, :]) + " | " + str(self.guessState[row, :]) + " | " + str(self.gameState[row, :])
        return string

    def overlaps(self, x, y, orientation, shipSize, board, allowAdjacent):
        # Check box with only ship
        if allowAdjacent:
            if orientation == 0:
                if sum(board[x,y:y+shipSize]) == 0: return False
            else:
                if sum(board[x:x+shipSize,y]) == 0: return False
        # Check box with padding around ship
        else:
            if orientation == 0:
                if sum(sum(board[max(x-1,0):x+2,max(y-1,0):min(y+shipSize+1, self.BOARD_SIZE)])) == 0: return False
            else:
                if sum(sum(board[max(x-1,0):min(x+shipSize+1, self.BOARD_SIZE),max(y-1,0):y+2])) == 0: return False
        return True

    ############################################################################
    # Evaluates the guess probability state.                                   #
    ############################################################################
    def evalBoard(self):
        self.probState = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        self.probTotal = 0

        # calculates count given all misses
        for ship in self.ships:
            if ship.sunk: continue
            shipSize = ship.size
            for orientation in range(2):
                if orientation == 0:
                    for x in range(self.BOARD_SIZE):
                        for y in range(self.BOARD_SIZE - shipSize + 1):
                            if self.overlaps(x, y, orientation, shipSize, self.guessState, True):
                                continue
                            if orientation == 0:
                                self.probState[x,y:y+shipSize] += 1
                            else:
                                self.probState[x:x+shipSize,y] += 1
                            self.probTotal += shipSize
                else:
                    for x in range(self.BOARD_SIZE - shipSize + 1):
                        for y in range(self.BOARD_SIZE):
                            if self.overlaps(x, y, orientation, shipSize, self.guessState, True):
                                continue
                            if orientation == 0:
                                self.probState[x,y:y+shipSize] += 1
                            else:
                                self.probState[x:x+shipSize,y] += 1
                            self.probTotal += shipSize
        # adds weighting to any hit zones

    def move(self, x, y):
        # if hit
        if self.hiddenState[x,y] == 1:
            print(f'({x},{y}) hit.')
            # find ship and do hit
            for ship in self.ships:
                if ship.overlap(x,y):
                    ship.hit(x,y)
                    if not ship.sunk:
                        self.gameState[x,y] = 2
                    elif self.allowAdjacent:
                        if ship.orientation == 0:
                            self.guessState[ship.x,ship.y:ship.y+ship.size] = 1
                            self.gameState[ship.x,ship.y:ship.y+ship.size] = 2
                        else:
                            self.guessState[ship.x:ship.x+ship.size,ship.y] = 1
                            self.gameState[ship.x:ship.x+ship.size,ship.y] = 1
                    else: 
                        if ship.orientation == 0:
                            self.guessState[max(ship.x-1,0):min(ship.x+2,self.BOARD_SIZE),max(ship.y-1,0):min(ship.y+ship.size+1,self.BOARD_SIZE)] = 1
                            self.gameState[max(ship.x-1,0):min(ship.x+2,self.BOARD_SIZE),max(ship.y-1,0):min(ship.y+ship.size+1,self.BOARD_SIZE)] = 1
                            self.gameState[ship.x,ship.y:ship.y+ship.size] = 2
                        else:
                            self.guessState[max(ship.x-1,0):min(ship.x+ship.size+1,self.BOARD_SIZE),max(ship.y-1,0):min(ship.y+2,self.BOARD_SIZE)] = 1
                            self.gameState[max(ship.x-1,0):min(ship.x+ship.size+1,self.BOARD_SIZE),max(ship.y-1,0):min(ship.y+2,self.BOARD_SIZE)] = 1
                            self.gameState[ship.x:ship.x+ship.size,ship.y] = 2
        # if miss
        else:
            print(f'({x},{y}) missed.')
            self.guessState[x,y] = 1
            self.gameState[x,y] = 1
            
        self.evalBoard()  
        print(self)
        print(self.probState)

class Ship():

    ############################################################################
    # Initiates the ship class.
    # size: length of the ship
    # x: The top left x coordinate
    # y: The top left y coordinate
    # orientation: 0 = horizontal (along y), 1 = vertical (along x)
    ############################################################################
    def __init__(self, size, x, y, orientation):
        self.size = size
        self.x = x
        self.y = y
        self.orientation = orientation
        self.sunk = False
        self.partsHit = [0] * size

    def __str__(self):
        return f'Ship of size {self.size} at ({self.x},{self.y}) facing direction {self.orientation}, sunk: {self.sunk}'

    def overlap(self, x, y):
        if self.orientation == 0:
            return self.y <= y < self.y+self.size and self.x == x
        else:
            return self.x <= x < self.x+self.size and self.y  == y
    
    def hit(self, x, y):
        if self.orientation == 0:
            self.partsHit[y - self.y] = 1
        else:
            self.partsHit[x - self.x] = 1
        print(f"{self} hit with remaining alive: {self.partsHit}")
        if sum(self.partsHit) == self.size:
            self.sunk = True
            print("Ship sunk.")
        

if __name__ == '__main__':
    ship1 = Battleship(True, False)