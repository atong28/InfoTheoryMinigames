# Info Theory Semester 1 Project Code

## Battleship Code Walkthrough

### Structure

The outermost layer is the Battleship Class, which is like the controlling class for the game. Upon a Battleship object initialization, the game runs. Manual mode is a way of analyzing a specific game, and automatic runs over many different games. In essence, they are the same, where the auto run applies the best move the algorithm gives. 

The main class is the Board class. I initialized the board with 4 different arrays: Hidden Board, Guess Board, Game Board, and Probability Board, for implementation. Here's what each does:

- Hidden Board: This stores the actual ship layout of the game. A 1 indicates a ship exists there, and a 0 indicates no ship.
- Guess Board: This stores the possibilities from the player guessing POV. A 1 indicates no hidden ship can exist there (either a miss or a sunken ship has been recorded.) 0, on the other hand, means possible. If there exists a hit, the value at that box is still 0 for the purposes of calculation.
- Game Board: This is what the player sees when they play the real Battleship game. A 0 indicates not checked, 1 indicates miss/not possible, and 2 indicates a hit on ship.
- Probability Board: This is to store the indexes of the ship likeliness at each point. The highest value is the next suggested value (and it favors top left in the case of tie, though arguably we could make this random, too.) If a ship has been hit but not sunk, there is an extremely large weighted value (in which the points not close to the hit become irrelevant, and we hunt for as long as possible to find the ship.) I'll clarify more about how this is calculated later.

The smallest class is the Ship class, to store details about individual ships. For efficiency, we'll be storing the top left corner's coordinates, the orientation (0 = horizontal, 1 = vertical) and the ship size. 

### Generating a Board

We'll be generating by selecting one possible orientation out of all the ships. If this overlaps with the current ships placed down, we will try again with a random orientation. This is probably not the most efficient, but it works enough.

### Evaluating Board State

This is the most important part. For the purposes of this algorithm, we wish to target the areas which have the greatest probabilities, or greatest ways a ship could fit onto the board. We'll iterate through each ship that currently is floating and not sunk, and iterate through every single possible position of each ship. If the layout is possible, we add 1 to each point the ship covers. From an empty board, then, obviously, the most probable spots are the 4 center spots. Now, the more important part: once a ship is hit, how do we handle the tracking?

Once we hit a ship, we should seek to sink the entire ship. Then, the nearest points are the most valuable, the 4 points in each direction. How should we weight this? There should certainly be greater weights to the left and right of a ship IF there has been 2 or more hits in a row. In other words, once we establish a line of ships, we believe that ship will keep extending until it is sunk. What I instead did was a multiplier to the previous part. Instead of adding 1 for every single ship layout, if the ship overlaps n points, we add 100n points to each point. In other words, if a possible 4-large ship overlays 2 known points hit, then we add 200 points to each point that the theoretical ship covers! We'll iterate through this to solve.

Once this part is evaluated, we make sure every single point hit but not sunk has a probability 0 so we don't produce repeated moves. Evaluating the board state is now done!

## Battleship To-Do

- Analyze the entropy per run.
- Create multithreading Battleship instances to run simulations faster.