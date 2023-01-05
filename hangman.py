from hangman_scripts import colors
from collections import defaultdict
import numpy as np

def matchesFilter(str, filter, used_letters):
    if len(str) != len(filter): return False
    
    for letter in used_letters:
        if letter in filter: continue
        if letter in str: return False
    
    for i in range(len(str)):
        if filter[i] == "█": 
            if str[i] in used_letters: return False
            continue
        
        if filter[i] != str[i]: return False
    return True

def getFilteredList(filter, wordlist, used_letters):
    newFilteredList = {word for word in wordlist if matchesFilter(word, filter, used_letters)}

    if len(newFilteredList) == 0:
        return {}
    
    return newFilteredList

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
            self.analyze_state()
            self.make_move()
                
        print(f"Congrats! You win in {self.counter} moves.")
    
    def analyze_state(self):
        print("Analyzing state: ")
        viable = self.evaluate_available_words()
        print("Number of possibilities for each word:")
        words = []
        for i in range(len(viable)):
            print(f"{self.words[i]} has {len(viable[i])} possibilities.")
            words += viable[i]

        # if too many possibilities, ask another letter

        arr = np.zeros((len(words), len(words)), dtype=float)

        # evaluate probabilities and run HMM

        # return most likely phrase and associated probability

        # find the next best letter

    def evaluate_available_words(self):
        viable = []
        for word in self.words:
            viable.append(getFilteredList(word, VOCAB[str(len(word))], self.letters_used))
        return viable

    def make_move(self, guess=""):

        if not guess:
            guess = input("Guess a letter -> ").lower()
        self.counter += 1
        
        # correct guess
        if guess in self.secret and guess not in self.letters_used:
            print(f"{colors.BOLD + colors.GREEN}Correct guess")
            self.letters_used += [guess]
            print(f"{colors.BOLD + colors.BLUE}Progress: {self.progress_updater(guess)}")
            print(f"{colors.BOLD + colors.YELLOW}Letters used: "+ (", ".join(self.letters_used)))
            
        # incorrect guess
        elif guess not in self.secret and guess not in self.letters_used:
            print(f"{colors.BOLD + colors.RED}Incorrect guess")
            self.letters_used += [guess]
            print(f"{colors.BOLD + colors.BLUE}Progress: " + (" ".join(self.progress)))
            print(f"{colors.BOLD + colors.YELLOW}Letters used: "+ (", ".join(self.letters_used)))
            
        # invalid input
        else:
            print(f"{colors.BOLD + colors.RED}Already used or invalid. Try again")
            self.counter -= 1

        self.words = "".join(self.progress).split(" ")
    
    # update the progress left
    def progress_updater(self, guess):
        for i in range(len(self.secret)):
            if guess == self.secret[i]: 
                self.progress[i] = guess
                self.letters_left -= 1
        return " ".join(self.progress)
    
    

if __name__ == '__main__':
    for line in open('vocabStrict.txt').readlines():
        word = line.strip()
        VOCAB[str(len(word))].append(word)

    secret = input("What is the secret? Enter here: ")
    game = Hangman(secret.lower())