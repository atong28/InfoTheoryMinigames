class Hangman():

    def __init__(self, secret):
        self.secret = secret
        self.counter = 0
        self.letters_used = []
        
        self.letters_left = len(self.secret)
        self.progress = ["█"] * self.letters_left
        
        self.core_game()
    
    def core_game(self):
        
        print(f"Phrase: " + ("".join(self.progress)))
        
        while self.letters_left > 0:
            guess = input("Guess a letter -> ")
            self.counter += 1
            
            # correct guess
            if guess in self.secret and guess not in self.letters_used:
                print("Correct guess")
                self.letters_used += [guess]
                print(f"Progress: {self.progress_updater(guess)}")
                print(f"Letters used: {self.letters_used}")
                
            # incorrect guess
            elif guess not in self.secret and guess not in self.letters_used:
                print("Incorrect guess")
                self.letters_used += [guess]
                print("Progress: " + ("".join(self.progress)))
                print(f"Letters used: {self.letters_used}")
                
            # invalid input
            else:
                print("Already used or invalid. Try again")
                self.counter -= 1
                
        print(f"Congrats! You win in {self.counter} moves.")
    
    # update the progress left
    def progress_updater(self, guess):
        for i in range(len(self.secret)):
            if guess == self.secret[i]: 
                self.progress[i] = guess
                self.letters_left -= 1
        return "".join(self.progress)

if __name__ == '__main__':

    secret = input("What is the secret? Enter here: ")
    game = Hangman(secret.lower())