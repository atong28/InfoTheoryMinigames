#import hangman.lib.colors as bcolors
from collections import defaultdict

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

VOCAB = defaultdict(lambda: [])

class Hangman():

    def __init__(self, secret):
        self.secret = secret
        self.counter = 1
        self.letters_used = []
        
        self.letters_left = len(self.secret)
        self.progress = ["█"] * self.letters_left

        self.make_move(" ")
        self.make_move("e")
        self.make_move("a")
        self.make_move("i")
        self.make_move("s")
        self.make_move("r")
        
        self.core_game_stage_two()
    
    def core_game_stage_two(self):
        
        print(f"Phrase: " + (" ".join(self.progress)))
        
        while self.letters_left > 0:
            viable = self.evaluate_available_words()
            self.make_move()
                
        print(f"Congrats! You win in {self.counter} moves.")
    
    def evaluate_available_words(self):
        viable = []
        

    def make_move(self, guess=""):

        if not guess:
            guess = input("Guess a letter -> ").lower()
        self.counter += 1
        
        # correct guess
        if guess in self.secret and guess not in self.letters_used:
            print(f"{bcolors.BOLD + bcolors.GREEN}Correct guess")
            self.letters_used += [guess]
            print(f"{bcolors.BOLD + bcolors.BLUE}Progress: {self.progress_updater(guess)}")
            print(f"{bcolors.BOLD + bcolors.YELLOW}Letters used: {self.letters_used}")
            
        # incorrect guess
        elif guess not in self.secret and guess not in self.letters_used:
            print(f"{bcolors.BOLD + bcolors.RED}Incorrect guess")
            self.letters_used += [guess]
            print(f"{bcolors.BOLD + bcolors.BLUE}Progress: " + (" ".join(self.progress)))
            print(f"{bcolors.BOLD + bcolors.YELLOW}Letters used: {self.letters_used}")
            
        # invalid input
        else:
            print(f"{bcolors.BOLD + bcolors.RED}Already used or invalid. Try again")
            self.counter -= 1
    
    # update the progress left
    def progress_updater(self, guess):
        for i in range(len(self.secret)):
            if guess == self.secret[i]: 
                self.progress[i] = guess
                self.letters_left -= 1
        return " ".join(self.progress)
    
    def analyze_state(self):
        print("Analyzing state: ")
        
        # find the wordlengths for each word.

if __name__ == '__main__':
    for line in open('vocab.txt').readlines():
        word = line.strip()
        VOCAB[str(len(word))].append(word)

    secret = input("What is the secret? Enter here: ")
    game = Hangman(secret.lower())