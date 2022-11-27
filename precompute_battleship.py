import numpy as np
import time
import json

start = time.time()

valid_arrangements = []

'''
0-1: Orientation (0 = horizontal, 1 = vertical)
0-9: First ship coordinate (if o=0, x coordinate; o=1 means y coordinate)
0-5: First ship coordinate (if o=0, y coordinate; o=1 means x coordinate)

0-1
0-9
0-6

0-1
0-9
0-7

0-1
0-9
0-7

0-1
0-9
0-8
'''

# generator function for seeding

ship_sizes = [5, 4, 3, 3, 2]

def nextSeed(recursion_depth, seed):
    for i in range(2):
        for j in range(10):
            for k in range(11 - ship_sizes[recursion_depth]):
                if recursion_depth == len(ship_sizes)-1:
                    yield 1000 * seed + 100 * i + 10 * j + k
                else:
                    for newSeed in nextSeed(recursion_depth + 1, 1000 * seed + 100 * i + 10 * j + k):
                        yield newSeed

def placeShip(orientation, length, width, size, board):
    if orientation == 0:
        board[length,width:width+size] = 1
    else:
        board[width:width+size,length] = 1
        

def isValid(seed):
    board = np.zeros((10, 10), dtype=int)
    
    for i in range(len(ship_sizes)):      
        placeShip(seed[3*i], seed[3*i+1], seed[3*i+2], ship_sizes[i], board)
    
    return sum(sum(board)) == sum(ship_sizes)
    

for newSeed in nextSeed(0, 0):
    arr = [eval(i) for i in str(newSeed).zfill(3*len(ship_sizes))]
    
    if isValid(arr):
        valid_arrangements += [str(newSeed).zfill(3*len(ship_sizes))]

end = time.time()

with open('valid_seeds.json', 'w') as f:
    json.dump(valid_arrangements, f)

print(f"Done in {end-start} seconds.")

