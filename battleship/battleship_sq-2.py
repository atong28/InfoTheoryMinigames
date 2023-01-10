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

    ############################################################################
    # Runs the Battleship game.                                                #
    ############################################################################
    def __init__(self, generateRandom, manual, games=1):
        self.board = Board(generateRandom)
        self.counter = 0
        self.win = False
        self.autoMove = unravel_index(self.board.probState.argmax(), self.board.probState.shape)
        self.autoResults = np.zeros(100, dtype=int)
        self.autoRounds = games

        # if manual, just run one round; play moves until win
        if manual:

            # print information
            print(self.board)

            if self.board.hitMode:
                print(f"{bcolors.BOLD + bcolors.GREEN}HIT MODE: Next best move at ({self.autoMove[0]},{self.autoMove[1]}).")         
            else:
                print(f"{bcolors.BOLD + bcolors.BLUE}SEARCH MODE: Next best move at ({self.autoMove[0]},{self.autoMove[1]}).")   

            # launch!
            while not self.win:
                self.playManual()
            print(f"Congratulations, you won in {self.counter} moves!")
            
        # run and reset after each game
        else:
            for i in range(self.autoRounds):
                if i % 100 == 0: print(f"{bcolors.CYAN}Run {i} completed.")
                while not self.win:
                    self.playAuto()
                self.autoResults[self.counter] += 1
                self.board.reset()
                self.board.generate()
                self.counter = 0
                self.win = False
            
            # analyze stats
            expectedMoves = 0
            print(f"{bcolors.BLUE + bcolors.BOLD}In {self.autoRounds} simulations, here is the distribution of game moves:")
            for i in range(100):
                if self.autoResults[i] == 0: continue
                print(f"{bcolors.GREEN}{i} moves: {self.autoResults[i]} game(s)")
                expectedMoves += i * self.autoResults[i] / self.autoRounds
                
            print(f"{bcolors.BLUE + bcolors.BOLD}The number of mean moves was {bcolors.YELLOW}{expectedMoves}.")
            
            # print for google sheets formatting
            printSheet = ""
            while (len(printSheet) != 1) and (printSheet != "y" and printSheet != "n"):
                printSheet = str.lower(input(f"{bcolors.BLUE + bcolors.BOLD}Would you like to print the list for spreadsheet formatting? Press Y for yes, N for no. First starts at 0. "))
            if printSheet == "y":
                for i in range(100):
                    print(self.autoResults[i])
        
    ############################################################################
    # Plays one move in manual mode.                                           #
    ############################################################################
    def playManual(self):
        nextMove = tuple(input("Enter row, col [format: xy, where x:[0,9], y:[0,9]]: "))
        self.board.move(int(nextMove[0]), int(nextMove[1]))
        self.counter += 1
        
        # print information
        print(self.board)

        if self.board.hitMode:
            print(f"{bcolors.BOLD + bcolors.GREEN}HIT MODE")         
        else:
            print(f"{bcolors.BOLD + bcolors.BLUE}SEARCH MODE")   

        i = (-self.board.probState).argsort(axis=None, kind='mergesort')
        j = np.unravel_index(i, self.board.probState.shape)
        sort = np.vstack(j).T

        bestMove = sort[0]

        if not self.board.hitMode:
            for move in sort:
                if self.board.probState[move[0],move[1]] == 0: break
                if (move[0] + move[1]) % 2 == 0:
                    bestMove = move
                    break

        

        #bestMove = unravel_index(self.board.probState.argmax(), self.board.probState.shape)
        print(f'Next best move at ({bestMove[0]},{bestMove[1]}).')

        # check for win
        for ship in self.board.ships:
            if not ship.sunk:
                return
        self.win = True

    ############################################################################
    # Plays one move in auto mode.                                             #
    ############################################################################
    def playAuto(self):
        self.board.move(self.autoMove[0],self.autoMove[1])
        self.counter += 1
        
        #nextMove = tuple(str(np.argmax(self.board.probState)).zfill(2))

        i = (-self.board.probState).argsort(axis=None, kind='mergesort')
        j = np.unravel_index(i, self.board.probState.shape)
        sort = np.vstack(j).T

        nextMove = sort[0]

        if not self.board.hitMode:
            for move in sort:
                if self.board.probState[move[0],move[1]] == 0: break
                if (move[0] + move[1]) % 2 == 0:
                    nextMove = move
                    break

        self.autoMove = nextMove

        # Check for win
        for ship in self.board.ships:
            if not ship.sunk:
                return
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
        if self.generateRandom:
            self.generate()
        else:
            for ship in self.DEFAULT_SHIP_SIZES:
                result = tuple(input(f"Input the coordinates and orientation for ship of size {ship} e.g. [xyo], [12h], [34v]: "))
                
                x = int(result[0])
                y = int(result[1])
                o = 0
                if result[2] == 'v': o = 1
                
                if o == 0:
                    self.hiddenState[x,y:y+ship] = 1
                else:
                    self.hiddenState[x:x+ship,y] = 1
                self.ships.append(Ship(ship, x, y, o))
        self.probState, self.probTotal = evalBoard(self, self.gameState, self.guessState)

    ############################################################################
    # Resets the board state.                                                  #
    # Clears hiddenState, guessState, ships                                    #
    ############################################################################
    def reset(self):
        self.hiddenState = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        self.guessState = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        self.gameState = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
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

                if not overlaps(x, y, orientation, shipSize, self.hiddenState):
                    if orientation == 0:
                        self.hiddenState[x,y:y+shipSize] = 1
                    else:
                        self.hiddenState[x:x+shipSize,y] = 1
                    break
            self.ships.append(Ship(shipSize, x, y, orientation))

    ############################################################################
    # String representation of the board state.                                #
    ############################################################################
    def __str__(self):

        # board values
        string = f'''{bcolors.BOLD+bcolors.YELLOW+bcolors.UNDERLINE}    HIDDEN BOARD          GUESS BOARD           GAME BOARD     '''
        for row in range(self.BOARD_SIZE):
            string += f"{bcolors.RESET}\n"
            for i in range(self.BOARD_SIZE):
                match self.hiddenState[row,i]:
                    case 0:
                        string += f"{bcolors.BLUE}0 "
                    case 1:
                        string += f"{bcolors.RED}1 "
            string += f"{bcolors.RESET}| "
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
    def move(self, x, y):

        # if hit
        if self.hiddenState[x,y] == 1:
            
            # find ship and do hit
            for ship in self.ships:
                if ship.overlap(x,y):
                    
                    # update ship hit
                    ship.hit(x,y)
                    
                    # guessState should remain 0 for purposes of algorithm
                    if not ship.sunk:
                        self.gameState[x,y] = 2
                        continue
                    
                    # if ship is sunk, update board states
                    if ship.orientation == 0:
                        self.guessState[ship.x,ship.y:ship.y+ship.size] = 1
                        self.gameState[ship.x,ship.y:ship.y+ship.size] = 2
                    else:
                        self.guessState[ship.x:ship.x+ship.size,ship.y] = 1
                        self.gameState[ship.x:ship.x+ship.size,ship.y] = 2
                            
        # if miss
        else:
            self.guessState[x,y] = 1
            self.gameState[x,y] = 1
            
        # re-evaluate the board in new state
        self.probState, self.probTotal = evalBoard(self, self.gameState, self.guessState)

################################################################################
# SHIP CLASS: Stores individual ship object information.                       #
# ---------------------------------------------------------------------------- #
# INSTANCE VARIABLES:                                                          #
# x, y: Coordinates of the top lerft corner of the ship.                       #
# orientation: 0 = horizontal (along the y-axis), 1 = vertical (along x-axis)  #
# sunk: True if the ship is fully sunk.                                        #
# partsHit: An array, 1 if the part of the ship has been hit, 0 otherwise      #
################################################################################
class Ship():
    def __init__(self, size, x, y, orientation):
        self.size = size
        self.x = x
        self.y = y
        self.orientation = orientation
        self.sunk = False
        self.partsHit = [0] * size

    def __str__(self):
        return f'Ship of size {self.size} at ({self.x},{self.y}) facing direction {self.orientation}, sunk: {self.sunk}'

    ############################################################################
    # Returns true if the provided coordinate is on the ship.                  #
    ############################################################################
    def overlap(self, x, y):
        if self.orientation == 0:
            return self.y <= y < self.y+self.size and self.x == x
        else:
            return self.x <= x < self.x+self.size and self.y  == y
    
    ############################################################################
    # Updates instance variables when it is hit at the given coordinates.      #
    # Doesn't check whether the x,y are valid. Make sure to precede with       #
    # the overlap function.                                                    #
    ############################################################################
    def hit(self, x, y):
        if self.orientation == 0:
            self.partsHit[y - self.y] = 1
        else:
            self.partsHit[x - self.x] = 1
        if sum(self.partsHit) == self.size:
            self.sunk = True

def run(numRounds):
    game = Battleship(generateRandom, manualMode, numRounds)

if __name__ == '__main__':
    print(f"{bcolors.MAGENTA+bcolors.BOLD+bcolors.UNDERLINE}                                   WELCOME TO BATTLESHIP!")
    print(f"{bcolors.RESET+bcolors.MAGENTA+bcolors.BOLD}=========================================================================================")
    
    # parse random generation rule
    gen = ""
    generateRandom = False
    manualMode = True
    numRounds = 1
    while (len(gen) != 1) and (gen != "y" and gen != "n"):
        gen = str.lower(input(f"{bcolors.CYAN}Would you like to generate a board randomly? Press Y for random, N for manual generation. "))
    if gen == "y": 
        generateRandom = True
    
        # parse manual mode rule
        manual = ""
        while (len(manual) != 1) and (manual != "y" and manual != "n"):
            manual = str.lower(input(f"{bcolors.CYAN}Would you like run the mode manually or automatically run for more results? Press Y for manual, N for auto. "))
        if manual == "n": 
            manualMode = False
            # find number
            while True:
                try:
                    numRounds = int(input(f"{bcolors.CYAN}How many rounds would you like to run? "))
                finally:
                    break

    # run it!
    run(numRounds)