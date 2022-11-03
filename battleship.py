import argparse
import time
import os
import numpy as np

class Battleship():

    def __init__(self, generateRandom, allowAdjacent):
        self.board = Board(generateRandom, allowAdjacent)
        self.board.evalBoard()
        print(self.board.probabilityState)

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
#                   not yet guessed. 1 indicates hit ship. 2 indicates missed. #
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

        self.evalBoard()

        print(self.probabilityState)

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
        self.probabilityState = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        self.ships = []

    ############################################################################
    # Generates an orientation of ships by random. Only used after a reset.    #
    # adjacent: True if ships may touch. False if ships cannot.                #
    ############################################################################
    def generate(self):
        for shipSize in self.DEFAULT_SHIP_SIZES:

            while True:
                orientation = np.random.randint(2)
                
                if orientation == 0:
                    x = np.random.randint(self.BOARD_SIZE)
                    y = np.random.randint(self.BOARD_SIZE - shipSize + 1)
                else:
                    x = np.random.randint(self.BOARD_SIZE - shipSize + 1)
                    y = np.random.randint(self.BOARD_SIZE)

                if not self.overlaps(x, y, orientation, shipSize, self.hiddenState):
                    if orientation == 0:
                        self.hiddenState[x,y:y+shipSize] = 1
                    else:
                        self.hiddenState[x:x+shipSize,y] = 1
                    break
            self.ships.append(Ship(shipSize, x, y, orientation))
            print(self.ships[-1])

    ############################################################################
    # Prints the board state.                                                  #
    ############################################################################
    def __str__(self):
        string = '''HIDDEN BOARD            GUESS BOARD'''
        for row in range(self.BOARD_SIZE):
            string += "\n"+str(self.hiddenState[row, :]) + " | " + str(self.guessState[row, :])
        return string

    def overlaps(self, x, y, orientation, shipSize, board):
        # Check box with only ship
        if self.allowAdjacent:
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
        self.probabilityState = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        self.probabilityTotal = 0
        for shipSize in self.DEFAULT_SHIP_SIZES:
            for orientation in range(2):
                if orientation == 0:
                    for x in range(self.BOARD_SIZE):
                        for y in range(self.BOARD_SIZE - shipSize + 1):
                            if self.overlaps(x, y, orientation, shipSize, self.guessState):
                                continue
                            if orientation == 0:
                                self.probabilityState[x,y:y+shipSize] += 1
                            else:
                                self.probabilityState[x:x+shipSize,y] += 1
                            self.probabilityTotal += shipSize
                else:
                    for x in range(self.BOARD_SIZE - shipSize + 1):
                        for y in range(self.BOARD_SIZE):
                            if self.overlaps(x, y, orientation, shipSize, self.guessState):
                                continue
                            if orientation == 0:
                                self.probabilityState[x,y:y+shipSize] += 1
                            else:
                                self.probabilityState[x:x+shipSize,y] += 1
                            self.probabilityTotal += shipSize



class Ship():

    ############################################################################
    # Initiates the ship class.
    # size: length of the ship
    # x: The top left x coordinate
    # y: The top left y coordinate
    # orientation: 0 = horizontal, 1 = vertical
    ############################################################################
    def __init__(self, size, x, y, orientation):
        self.size = size
        self.x = x
        self.y = y
        self.orientation = orientation

    def __str__(self):
        return f'Ship of size {self.size} at ({self.x},{self.y}) facing direction {self.orientation}'
    

if __name__ == '__main__':
    ship1 = Battleship(True, False)