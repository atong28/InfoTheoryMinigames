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

# load into memory the wordlist

f = open('top50k.txt', 'r', encoding='utf-8')
content = f.read()

print("Loading words...")

def splitText(entry):
    result = entry.split(" ")
    return (result[0], int(result[1]))

wordList = list(map(splitText, content.splitlines()))

sortedList = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

for word in wordList:
    if len(word[0]) > 59: print(word)
    sortedList[len(word[0])].append(word)
    
print("Loaded the top 50,000 entries!")

class Hangman():

    def __init__(self, secret):
        self.secret = secret
        self.counter = 1
        self.letters_used = []
        
        self.letters_left = len(self.secret)
        self.progress = ["█"] * self.letters_left
        
        self.core_game()
    
    def core_game(self):
        
        print(f"Phrase: " + (" ".join(self.progress)))
        
        print(f"Q1: What spaces are there? ")
        self.make_move()
        
        
        
        while self.letters_left > 0:
            self.make_move()
                
        print(f"Congrats! You win in {self.counter} moves.")
    
    def make_move(self):
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

    secret = input("What is the secret? Enter here: ")
    game = Hangman(secret.lower())