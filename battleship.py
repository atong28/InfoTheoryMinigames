import numpy as np
from numpy import unravel_index
import math

################################################################################
# Text color presets.                                                          #
################################################################################
class bcolors:
    RED = '\u001b[31;1m'
    BLUE = '\u001b[34;1m'
    YELLOW = '\u001b[33;1m'
    GREEN = '\u001b[32;1m'
    MAGENTA = '\u001b[35;1m'
    CYAN = '\u001b[36;1m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\u001b[0m'

################################################################################
# Calculates the entropy of the board probability state.                       #
################################################################################
def entropy(board):
    infoBoard = np.zeros((board[0].size, board[0].size), dtype=float)
    for i in range(board[0].size):
        for j in range(board[0].size):
            if board[i,j]==0: continue
            infoBoard[i,j] = board[i,j] * math.log2(1/board[i,j])
    return infoBoard

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
    def __init__(self, generateRandom, allowAdjacent, manual):
        self.board = Board(generateRandom, allowAdjacent)
        self.counter = 0
        self.win = False
        self.autoMove = unravel_index(self.board.probState.argmax(), self.board.probState.shape)
        self.autoResults = np.zeros(100, dtype=int)
        
        # modifiable
        self.autoRounds = 100000

        # if manual, just run one round; play moves until win
        if manual:

            # print information
            print(self.board)

            if self.board.hitMode:
                print(f"{bcolors.BOLD + bcolors.GREEN}HIT MODE: {sum(sum(self.board.eMatrix))} expected bits till end.")         
            else:
                print(f"{bcolors.BOLD + bcolors.BLUE}SEARCH MODE: {sum(sum(self.board.eMatrix))} expected bits till game completion.")   

            print(f'Next best move at ({self.autoMove[0]},{self.autoMove[1]}), reducing by {self.board.eMatrix[int(self.autoMove[0]),int(self.autoMove[1])]} bits')

            # launch!
            while not self.win:
                self.playManual()
            print(f"Congratulations, you won in {self.counter} moves!")
            
        # run and reset after each game
        else:
            for i in range(self.autoRounds):
                if i % 100 == 0: print(f"Run {i} completed.")
                while not self.win:
                    self.playAuto()
                self.autoResults[self.counter] += 1
                self.board.reset()
                self.board.generate()
                self.counter = 0
                self.win = False
            
            # analyze stats
            expectedMoves = 0
            print(f"In {self.autoRounds} simulations, here is the distribution of game moves:")
            for i in range(100):
                if self.autoResults[i] == 0: continue
                print(f"{i} moves: {self.autoResults[i]} games")
                expectedMoves += i * self.autoResults[i] / self.autoRounds
                
            print(f"The number of mean moves was {expectedMoves}.")
            
            # print for google sheets formatting
            printSheet = ""
            while (len(printSheet) != 1) and (printSheet != "y" and printSheet != "n"):
                printSheet = str.lower(input("Would you like to print the list for spreadsheet formatting? Press Y for yes, N for no. First starts at 0. "))
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
            print(f"{bcolors.BOLD + bcolors.GREEN}HIT MODE: {sum(sum(self.board.eMatrix))} expected bits till end.")         
        else:
            print(f"{bcolors.BOLD + bcolors.BLUE}SEARCH MODE: {sum(sum(self.board.eMatrix))} expected bits till game completion.")   

        bestMove = unravel_index(self.board.probState.argmax(), self.board.probState.shape)
        print(f'Next best move at ({bestMove[0]},{bestMove[1]}), reducing by {self.board.eMatrix[int(bestMove[0]),int(bestMove[1])]} bits')

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
        
        nextMove = tuple(str(np.argmax(self.board.probState)).zfill(2))
        self.autoMove = (int(nextMove[0]), int(nextMove[1]))

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
# - allowAdjacent:  True if ships are allowed to 'touch'. False if not.        #
################################################################################
class Board():
    BOARD_SIZE = 10
    DEFAULT_SHIP_SIZES = [5,4,3,3,2]
    
    ############################################################################
    # Initiates a board. Resets first, then generates, and then evaluates.     #
    ############################################################################
    def __init__(self, generateRandom, allowAdjacent):

        self.generateRandom = generateRandom
        self.allowAdjacent = allowAdjacent
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
        self.evalBoard()

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

                if not self.overlaps(x, y, orientation, shipSize, self.hiddenState, self.allowAdjacent):
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
        string += f'\n{bcolors.BOLD+bcolors.YELLOW+bcolors.UNDERLINE}                      INFORMATION MATRIX                       '
        colorMatrix = self.eMatrix / np.amax(self.eMatrix) * 24
        string += bcolors.RESET
        for i in range(self.BOARD_SIZE):
            string += '\n  '
            for j in range(self.BOARD_SIZE):
                if int(colorMatrix[i,j]) == 24:
                    colorMatrix[i,j] -= 1
                string += f"\033[38;5;{232 + int(colorMatrix[i,j])}m{str(round(self.eMatrix[i,j],3)).ljust(5, '0')} "
        return string

    def overlaps(self, x, y, orientation, shipSize, board, allowAdjacent):
        # check box with only ship
        if allowAdjacent:
            if orientation == 0:
                if sum(board[x,y:y+shipSize]) == 0: return False
            else:
                if sum(board[x:x+shipSize,y]) == 0: return False
        # check box with padding around ship
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

        self.hitMode = False

        # calculates count given all misses
        for ship in self.ships:
            if ship.sunk: continue
            ship.size
            for orientation in range(2):
                if orientation == 0:
                    for x in range(self.BOARD_SIZE):
                        for y in range(self.BOARD_SIZE - ship.size + 1):
                            # if the ship collides with a miss block or a sunken ship block, it is not a valid location
                            if self.overlaps(x, y, orientation, ship.size, self.guessState, True):
                                continue
                            
                            # since the ship is a valid placement, if the sum here is positive, it travels over a hit but not sunk ship
                            if sum(self.gameState[x,y:y+ship.size]) > 0:
                                # add probability given how many hit points the ship traverses over (1 hit point, sum = 2; 2 hit point, sum = 4)
                                self.hitMode = True
                                self.probState[x,y:y+ship.size] += 50 * sum(self.gameState[x,y:y+ship.size])
                            # otherwise, add small probability
                            else:
                                self.probState[x,y:y+ship.size] += 1
                            
                else:
                    for x in range(self.BOARD_SIZE - ship.size + 1):
                        for y in range(self.BOARD_SIZE):
                            if self.overlaps(x, y, orientation, ship.size, self.guessState, True):
                                continue
                            # since the ship is a valid placement, if the sum here is positive, it travels over a hit but not sunk ship
                            if sum(self.gameState[x:x+ship.size,y]) > 0:
                                # add probability given how many hit points the ship traverses over (1 hit point, sum = 2; 2 hit point, sum = 4)
                                self.hitMode = True
                                self.probState[x:x+ship.size,y] += 50 * sum(self.gameState[x:x+ship.size,y])
                            # otherwise, add small probability
                            else:
                                self.probState[x:x+ship.size,y] += 1
        # removes probability for ships that are already hit but not sunk, and if in hitMode, sets nonnear values to 0
        for x in range(self.BOARD_SIZE):
            for y in range(self.BOARD_SIZE):
                if self.hitMode and self.probState[x,y] < 100:
                    self.probState[x,y] = 0
                if self.gameState[x,y] == 2 and self.guessState[x,y] == 0:
                    self.probState[x,y] = 0
                    
        self.probTotal = sum(sum(self.probState))
        if self.probTotal == 0:
            self.eMatrix = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=float)
            return
        pMatrix = self.probState / self.probTotal
        self.eMatrix = entropy(pMatrix)

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
                        
                    # if ship is sunk, update board states depending on allowAdjacent rule
                    elif self.allowAdjacent:
                        if ship.orientation == 0:
                            self.guessState[ship.x,ship.y:ship.y+ship.size] = 1
                            self.gameState[ship.x,ship.y:ship.y+ship.size] = 2
                        else:
                            self.guessState[ship.x:ship.x+ship.size,ship.y] = 1
                            self.gameState[ship.x:ship.x+ship.size,ship.y] = 2
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
            self.guessState[x,y] = 1
            self.gameState[x,y] = 1
            
        # re-evaluate the board in new state
        self.evalBoard()

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
        

if __name__ == '__main__':
    print(f"{bcolors.MAGENTA+bcolors.BOLD+bcolors.UNDERLINE}                                   WELCOME TO BATTLESHIP!")
    print(f"{bcolors.RESET+bcolors.MAGENTA+bcolors.BOLD}=========================================================================================")
    
    # parse random generation rule
    gen = ""
    generateRandom = False
    while (len(gen) != 1) and (gen != "y" and gen != "n"):
        gen = str.lower(input(f"{bcolors.CYAN}Would you like to generate a board randomly? Press Y for random, N for manual generation. "))
    if gen == "y": generateRandom = True
    
    # parse allow adjacent rule
    allowAdj = ""
    allowAdjacent = False
    while (len(allowAdj) != 1) and (allowAdj != "y" and allowAdj != "n"):
        allowAdj = str.lower(input(f"{bcolors.CYAN}Would you like to allow ships to touch? Press Y for yes, N for no. "))
    if allowAdj == "y": allowAdjacent = True
    
    # parse manual mode rule
    manual = ""
    manualMode = False
    while (len(manual) != 1) and (manual != "y" and manual != "n"):
        manual = str.lower(input(f"{bcolors.CYAN}Would you like run the mode manually or automatically run for more results? Press Y for manual, N for auto. "))
    if manual == "y": manualMode = True
    
    # run it!
    ship = Battleship(generateRandom, allowAdjacent, manualMode)