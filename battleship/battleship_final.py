import numpy as np
from numpy import unravel_index
import lib.colors as bcolors

################################################################################
# Evaluates the guess probability state.                                       #
################################################################################
def evalBoard(game, gameState, guessState):
    probState = np.zeros((Board.BOARD_SIZE, Board.BOARD_SIZE), dtype=int)
    probTotal = 0

    game.hitMode = False

    # calculates count given all misses
    for ship in game.ships:
        if ship.sunk: continue

        # test for all horizontal
        orientation = 0
        for x in range(Board.BOARD_SIZE):
            for y in range(Board.BOARD_SIZE - ship.size + 1):

                # if the ship collides with a miss block or a sunken ship block, it is not a valid location
                if overlaps(x, y, orientation, ship.size, guessState): continue
                
                # since the ship is a valid placement, if the sum here is positive, it travels over a hit but not sunk ship
                if sum(gameState[x,y:y+ship.size]) > 0:
                    # add probability given how many hit points the ship traverses over (1 hit point, sum = 2; 2 hit point, sum = 4)
                    game.hitMode = True
                    probState[x,y:y+ship.size] += 50 * (sum(gameState[x,y:y+ship.size]) ** 2)

                # otherwise, add small probability
                else:
                    probState[x,y:y+ship.size] += 1
        
        # test for all vertical
        orientation = 1
        for x in range(Board.BOARD_SIZE - ship.size + 1):
            for y in range(Board.BOARD_SIZE):
                if overlaps(x, y, orientation, ship.size, guessState): continue
                # since the ship is a valid placement, if the sum here is positive, it travels over a hit but not sunk ship
                if sum(gameState[x:x+ship.size,y]) > 0:
                    # add probability given how many hit points the ship traverses over (1 hit point, sum = 2; 2 hit point, sum = 4)
                    game.hitMode = True
                    probState[x:x+ship.size,y] += 50 * (sum(gameState[x:x+ship.size,y]) ** 2)
                # otherwise, add small probability
                else:
                    probState[x:x+ship.size,y] += 1

    # removes probability for ships that are already hit but not sunk, and if in hitMode, sets non-near values to 0
    for x in range(Board.BOARD_SIZE):
        for y in range(Board.BOARD_SIZE):
            if game.hitMode and probState[x,y] < 100:
                probState[x,y] = 0
            if gameState[x,y] == 2 and guessState[x,y] == 0:
                probState[x,y] = 0
                
    probTotal = sum(sum(probState))

    return probState, probTotal

################################################################################
# Tests if a ship overlaps a given board.                                      #
################################################################################
def overlaps(x, y, orientation, shipSize, board):
    if orientation == 0:
        if sum(board[x,y:y+shipSize]) == 0: return False
    else:
        if sum(board[x:x+shipSize,y]) == 0: return False
    return True

################################################################################
# BATTLESHIP CLASS: Runs the game.                                             #
# ---------------------------------------------------------------------------- #
# INSTANCE VARIABLES:                                                          #
# - board:   Stores the Board class that the game runs on.                     #
# - counter: Counts the number of moves the player has made.                   #
# - win:     True if player has won. Terminates the game.                      #
################################################################################
class Battleship():
    COORDINATES_X = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    COORDINATES_Y = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

    ############################################################################
    # Runs the Battleship game.                                                #
    ############################################################################
    def __init__(self):
        self.board = Board()
        self.counter = 0
        self.win = False
        self.autoMove = unravel_index(self.board.probState.argmax(), self.board.probState.shape) 
        self.shipsSunk = 0 

        # launch!
        while not self.win:
            self.playManual()
        print(f"Congratulations, you won in {self.counter} moves!")
        
    ############################################################################
    # Plays one move in manual mode.                                           #
    ############################################################################
    def playManual(self):
        self.counter += 1
        
        # print information
        print(self.board)

        if self.board.hitMode:
            print(f"{bcolors.BOLD + bcolors.GREEN}HIT MODE")         
        else:
            print(f"{bcolors.BOLD + bcolors.BLUE}SEARCH MODE")   

        bestMove = unravel_index(self.board.probState.argmax(), self.board.probState.shape)
        print(f'Shot #{self.counter}: Coordinate ({self.COORDINATES_X[bestMove[0]]},{self.COORDINATES_Y[bestMove[1]]}).')

        result = input("Result: ")
        match result:
            case "H":
                self.board.move(1, bestMove[0], bestMove[1])
            case "M":
                self.board.move(0, bestMove[0], bestMove[1])
            case "S":
                self.board.move(2, bestMove[0], bestMove[1])
                self.shipsSunk += 1

        # check for win
        if self.shipsSunk == 5:
            self.win = True

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
################################################################################
class Board():
    BOARD_SIZE = 10
    DEFAULT_SHIP_SIZES = [5,4,3,3,2]
    
    ############################################################################
    # Initiates a board. Resets first, then generates, and then evaluates.     #
    ############################################################################
    def __init__(self, generateRandom):

        self.generateRandom = generateRandom
        self.hitMode = False

        self.reset()
        self.probState, self.probTotal = evalBoard(self, self.gameState, self.guessState)

    ############################################################################
    # Resets the board state.                                                  #
    # Clears hiddenState, guessState, ships                                    #
    ############################################################################
    def reset(self):
        self.hiddenState = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        self.guessState = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        self.gameState = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        self.ships = [5, 4, 3, 3, 2]

    ############################################################################
    # String representation of the board state.                                #
    ############################################################################
    def __str__(self):

        # board values
        string = f'''{bcolors.BOLD+bcolors.YELLOW+bcolors.UNDERLINE}     GUESS BOARD           GAME BOARD     '''
        for row in range(self.BOARD_SIZE):
            string += f"{bcolors.RESET}\n"
            for i in range(self.BOARD_SIZE):
                match self.guessState[row,i]:
                    case 0:
                        string += f"{bcolors.BLUE}0 "
                    case 1:
                        string += f"{bcolors.RED}1 "
            string += f"{bcolors.RESET}| "
            for i in range(self.BOARD_SIZE):
                match self.gameState[row,i]:
                    case 0:
                        string += f"{bcolors.BLUE}0 "
                    case 1:
                        string += f"{bcolors.RED}1 "
                    case 2:
                        string += f"{bcolors.GREEN}2 "
        
        # if at the end of the game, do not print!
        if self.probTotal == 0: return string

        # print the information matrix values, color coded on greyscale of 24 values
        string += f'\n{bcolors.BOLD+bcolors.YELLOW+bcolors.UNDERLINE}                      PROBABILITY MATRIX                       '
        
        pMatrix = self.probState / self.probTotal

        colorMatrix = pMatrix / np.amax(pMatrix) * 7
        string += bcolors.RESET
        for i in range(self.BOARD_SIZE):
            string += '\n  '
            for j in range(self.BOARD_SIZE):
                string += f"\033[38;5;{248 + int(colorMatrix[i,j])}m{str(round(pMatrix[i,j],3)).ljust(5, '0')} "
        return string

    ############################################################################
    # Checks at (x,y) to see if a ship is hit.                                 #
    ############################################################################
    def move(self, action, x, y):
        
        
        match action:
            # if miss
            case 0:
                self.guessState[x,y] = 1
                self.gameState[x,y] = 1
            # if hit
            case 1:
                self.gameState[x,y] = 2
            # if sunk, find the neighboring squares and declare that ship as sunk
            case other:
                self.guessState[x,y]
            
        # re-evaluate the board in new state
        self.probState, self.probTotal = evalBoard(self, self.gameState, self.guessState)

def run():
    game = Battleship()

if __name__ == '__main__':
    print(f"{bcolors.MAGENTA+bcolors.BOLD+bcolors.UNDERLINE}                                   WELCOME TO BATTLESHIP!")
    print(f"{bcolors.RESET+bcolors.MAGENTA+bcolors.BOLD}=========================================================================================")

    # run it!
    run()