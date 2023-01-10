import numpy as np
from numpy import unravel_index
from battleship_scripts import colors
import copy
from collections import defaultdict

BOARD_SIZE = 10
DEFAULT_SHIP_SIZES = [5,4,3,3,2]

# returns true if in bounds
def check_bounds(coordinate):
    return 0 <= coordinate[0] < BOARD_SIZE and 0 <= coordinate[1] < BOARD_SIZE

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
    def __init__(self, generate_random, games=1):
        self.board = Board(generate_random)
        self.solution = Solution(self.board)
        self.results = np.zeros(100, dtype=int)
        self.rounds = games
        
        result = self.playAuto()
        
        print(f"It took {result} moves to complete the game.")
        
        '''for i in range(self.rounds):
            if i % 100 == 0: print(f"{bcolors.CYAN}Run {i} completed.")
            num_moves = self.playAuto()
            self.results[num_moves] += 1
            self.board = Board(generate_random)
        
        # analyze stats
        expectedMoves = 0
        print(f"{bcolors.BLUE + bcolors.BOLD}In {self.rounds} simulations, here is the distribution of game moves:")
        for i in range(100):
            if self.results[i] == 0: continue
            print(f"{bcolors.GREEN}{i} moves: {self.results[i]} game(s)")
            expectedMoves += i * self.results[i] / self.rounds
            
        print(f"{bcolors.BLUE + bcolors.BOLD}The number of mean moves was {bcolors.YELLOW}{expectedMoves}.")
        
        # print for google sheets formatting
        printSheet = ""
        while (len(printSheet) != 1) and (printSheet != "y" and printSheet != "n"):
            printSheet = str.lower(input(f"{bcolors.BLUE + bcolors.BOLD}Would you like to print the list for spreadsheet formatting? Press Y for yes, N for no. First starts at 0. "))
        if printSheet == "y":
            for i in range(100):
                print(self.results[i])'''

    ############################################################################
    # Plays one game in auto mode.                                             #
    ############################################################################
    def playAuto(self):
        return self.solution.run()
        
################################################################################
# SOLUTION CLASS:                                                              #
# ---------------------------------------------------------------------------- #
# CONSTANTS                                                                    #
# - board: A Board object                                                      #
# - instances: Instances of solutions created when sunk                        #
# - remaining_ships: List of the sizes of remaining ships                      #
# - game_state: An array storing values of the board.                          #
#    - 0: not tried                                                            #
#    - 1: missed                                                               #
#    - 2: hit                                                                  #
#    - 3: sunk                                                                 #
################################################################################
class Solution():
    
    ############################################################################
    # Initiates the solution instance.                                         #
    ############################################################################
    def __init__(self, board, game_state=np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int), remaining_ships=DEFAULT_SHIP_SIZES, instance_depth=0):
        self.board = board
        self.instances = defaultdict(lambda: 0)
        self.remaining_ships = remaining_ships
        self.game_state = game_state
        self.total_states = self.get_total_states()
        self.move_count = 0
        self.eval_on = False
        self.ships_sunk = 0
        self.instance_depth = instance_depth
        
    def get_total_states(self):
        # if instances are created, total is the sum of all of them
        if self.instances_created():
            return sum(self.instances.values())

        # if hit mode, cover with ghost ship and recursively generate cases
        if self.in_hit_mode():
            # impossible case; cannot still have hit points and have all ships sunk
            if self.instance_depth == 5:
                return 0
            total = 0
            for ship_size in self.remaining_ships:
                for pos in range(BOARD_SIZE):
                    for len in range(BOARD_SIZE - ship_size + 1):
                        # if the ship collides with missing or sunk, then it is not a valid location
                        if any(value in (1, 3) for value in self.game_state[pos,len:len+ship_size]): pass
                        # if it collides with hit point, it is a valid location
                        elif any(value == 2 for value in self.game_state[pos,len:len+ship_size]):
                            game_state = copy.deepcopy(self.game_state)
                            remaining_ships = copy.deepcopy(self.remaining_ships)
                            board = copy.deepcopy(self.board)
                            remaining_ships.remove(ship_size)
                            # find every point that contains a hit point and temp set as sunk
                            for i in range(ship_size):
                                if self.game_state[pos, len + i] == 2:
                                    game_state[pos, len + i] == 3
                            # find total states of a ghost solution instance with depth+1, add to the total
                            total += Solution(board, game_state, remaining_ships, self.instance_depth + 1).get_total_states()
                            
                        # do the same for the other orientation
                        if any(value in (0, 2) for value in self.game_state[len:len+ship_size,pos]): pass
                        elif any(value == 2 for value in self.game_state[len:len+ship_size,pos]):
                            game_state = copy.deepcopy(self.game_state)
                            remaining_ships = copy.deepcopy(self.remaining_ships)
                            board = copy.deepcopy(self.board)
                            remaining_ships.remove(ship_size)
                            for i in range(ship_size):
                                if self.game_state[len + i, pos] == 2:
                                    game_state[len + i, pos] == 3
                            total += Solution(board, game_state, remaining_ships, self.instance_depth + 1).get_total_states()
            return total

        total = 1
        # otherwise multiply together as normal
        for ship_size in self.remaining_ships:
            counter = 0
            for pos in range(BOARD_SIZE):
                for len in range(BOARD_SIZE - ship_size + 1):
                    # if the ship only collides with hit or not tried, then it is valid location
                    if all(value in (0, 2) for value in self.game_state[pos,len:len+ship_size]): counter += 1
                    if all(value in (0, 2) for value in self.game_state[len:len+ship_size,pos]): counter += 1
            total *= counter
        return total
    
    def run(self):
        while not self.check_win():
            self.move_count += 1
            
            # manual debug without eval
            if not self.eval_on:
                print(self.board)
                move = tuple(map(int, input("Enter row, col [format = x y]: ").split(' ')))
                self.move(move)
                continue
            
            p = self.eval_state()
            best_move = unravel_index(p.argmax(), p.shape)
            
            # execute move
            self.move(best_move)
            
        return self.move_count
        
    def eval_state(self):
        unfound_hit_points = sum(self.remaining_ships) - np.count_nonzero(self.game_state == 2)

        p = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=float)

        # if there are instances, iterate through all and sum together
        if self.instances_created():
            w = np.array(list(self.instances.values()))
            
            # normalize probability
            w /= sum(w)

            weights = {list(self.instances.keys())[i] : w[i] for i in range(len(w))}
            
            for instance in self.instances.keys():
                # add the weighted probability of the instance evaluation output
                p += weights[instance] * instance.eval_state()
            
            # return finalized normalized probabilities
            return p / sum(p) * unfound_hit_points
        
        # if in hit mode, only consider the combinations of ships that overlap a hit point
        if self.in_hit_mode():
            pass

        for ship_size in self.remaining_ships:
            for pos in range(BOARD_SIZE):
                for len in range(BOARD_SIZE - ship_size + 1):
                    # if the ship only collides with hit or not tried, then it is valid location; increment 1 at each location
                    if all(value in (0, 2) for value in self.game_state[pos,len:len+ship_size]):
                        p[pos, len:len+ship_size] += 1
                    if all(value in (0, 2) for value in self.game_state[len:len+ship_size,pos]):
                        p[len:len+ship_size, pos] += 1
        # return normalized matrix
        return p / sum(p) * unfound_hit_points
    
    def move(self, move, result):

        # if depth is exceeded and there are still hit points, the instance creation is impossible
        if self.instance_depth == 5 and self.in_hit_mode():
            return 0

        x = move[0]
        y = move[1]
        
        # when done manually, this is replaced with input function
        result = self.board.move(x, y)
        print(f"Result: {result}")

        # result must be applied to all instances. if no instances, this part is skipped
        for instance, total_cases in self.instances.values():
            if total_cases == 0: continue
            result = instance.move(move, result)
            # win has occurred
            if result == -1:
                # collapse own instance until at top level
                return -1
            else:
                self.instances[instance] = result
        
        match result:
            case 'M':
                self.game_state[x, y] = 1
            case 'H':
                self.game_state[x, y] = 2
            case 'S':
                self.ships_sunk += 1

                # check for win
                if self.check_win():
                    # signal win has occurred
                    return -1

                # search for squares next to it that are hit but not sunk
                for dir in ((-1, 0), (0, -1), (1, 0), (0, 1)):
                    coord = np.add(dir, move)
                    if check_bounds(coord) and self.game_state[coord[0], coord[1]] == 2:
                        break
                for ship_size in self.remaining_ships:
                    coord_border = np.add(np.multiply(dir, ship_size-1), move)
                    # valid ship orientation
                    if check_bounds(coord_border) and self.game_state[coord_border[0], coord_border[1]] == 2:
                        board = copy.deepcopy(self.board)
                        game_state = copy.deepcopy(self.game_state)
                        remaining_ships = copy.deepcopy(self.remaining_ships)
                        remaining_ships.remove(ship_size)
                        match dir:
                            case (-1, 0):
                                game_state[coord_border[0]:coord_border[0]+ship_size, y] = 3
                                
                            case (0, -1):
                                game_state[x, coord_border[1]:coord_border[1]+ship_size] = 3
                            case (1, 0):
                                game_state[coord[0]:coord[0]+ship_size, y] = 3
                            case (0, 1):
                                game_state[x, coord[1]+coord[1]+ship_size] = 3
                        self.instances.append(Solution(board, game_state, remaining_ships))
                # if no new instances are created, it must be impossible state
                if len(self.instances) == 0:
                    return 0
    
        total_states = self.get_total_states()
        return total_states
    
    def check_win(self):
        return self.ships_sunk == 5
    
    def instances_created(self):
        return len(self.instances) > 1

    def in_hit_mode(self):
        return 2 in self.game_state
        
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
    
    
    ############################################################################
    # Initiates a board.                                                       #
    ############################################################################
    def __init__(self, generateRandom):
        self.generateRandom = generateRandom

        self.reset()
        # random generation
        if self.generateRandom:
            self.generate()
        # manual generation
        else:
            for ship in DEFAULT_SHIP_SIZES:
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

    ############################################################################
    # Resets the board state.                                                  #
    # Clears hiddenState, guessState, ships                                    #
    ############################################################################
    def reset(self):
        self.hiddenState = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.ships = []

    ############################################################################
    # Generates an orientation of ships by random. Only used after a reset.    #
    # adjacent: True if ships may touch. False if ships cannot.                #
    ############################################################################
    def generate(self):
        for shipSize in DEFAULT_SHIP_SIZES:
            while True:
                orientation = np.random.randint(2)
                
                if orientation == 0:
                    x = np.random.randint(BOARD_SIZE)
                    y = np.random.randint(BOARD_SIZE - shipSize + 1)
                else:
                    x = np.random.randint(BOARD_SIZE - shipSize + 1)
                    y = np.random.randint(BOARD_SIZE)

                if not self.overlaps(x, y, orientation, shipSize):
                    if orientation == 0:
                        self.hiddenState[x,y:y+shipSize] = 1
                    else:
                        self.hiddenState[x:x+shipSize,y] = 1
                    break
            self.ships.append(Ship(shipSize, x, y, orientation))

    ############################################################################
    # Tests if a ship overlaps a given board.                                  #
    ############################################################################
    def overlaps(self, x, y, orientation, shipSize):
        if orientation == 0:
            if sum(self.hiddenState[x,y:y+shipSize]) == 0: return False
        else:
            if sum(self.hiddenState[x:x+shipSize,y]) == 0: return False
        return True

    ############################################################################
    # Checks at (x,y) to see if a ship is hit.                                 #
    ############################################################################
    def move(self, x, y):

        # if hit/sink
        if self.hiddenState[x,y] == 1:
            for ship in self.ships:
                if ship.overlap(x,y):
                    ship.hit(x,y)
                    if not ship.sunk:
                        return 'H'
                    return 'S'
        # if miss
        else:
            return 'M'
        
    def __str__(self):

        # board values
        string = f'''{colors.BOLD+colors.YELLOW+colors.UNDERLINE}    HIDDEN BOARD   '''
        for row in range(BOARD_SIZE):
            string += f"{colors.RESET}\n"
            for i in range(BOARD_SIZE):
                match self.hiddenState[row,i]:
                    case 0:
                        string += f"{colors.BLUE}o "
                    case 1:
                        string += f"{colors.RED}x "
                        
        return string

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
    game = Battleship(generateRandom, numRounds)

if __name__ == '__main__':
    print(f"{colors.MAGENTA+colors.BOLD+colors.UNDERLINE}                                   WELCOME TO BATTLESHIP!")
    print(f"{colors.RESET+colors.MAGENTA+colors.BOLD}=========================================================================================")
    
    # parse random generation rule
    gen = ""
    generateRandom = False
    manualMode = True
    numRounds = 1
    while (len(gen) != 1) and (gen != "y" and gen != "n"):
        gen = str.lower(input(f"{colors.CYAN}Would you like to generate a board randomly? Press Y for random, N for manual generation. "))
    if gen == "y": 
        generateRandom = True

    # run it!
    run(1)