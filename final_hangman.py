from hangman_scripts import colors, scripts
from collections import defaultdict
import numpy as np
from srilm import *

################################################################################
# Initialization.                                                              #
# VOCAB: The list of available vocabulary.                                     #
################################################################################
VOCAB = defaultdict(lambda: [])
np.set_printoptions(precision=3)
n = initLM(5)

################################################################################
# Hangman Class                                                                #
# ---------------------------------------------------------------------------- #
# can_lie: True if a lie has not yet been spoken.                              #
# counter: Stores the number of moves.                                         #
# length: Stores the length of the overall phrase.                             #
# letters_used: Stores the letters used, including punctuation.                #
# progress: List of characters in the phrase, with █ as the unknown character. #
# order: A few preset letters that motivates stage one.                        #
# fails: A list of phrases that have failed in guessing.                       #
################################################################################
class Hangman():

    ############################################################################
    # Initiates the game.                                                      #
    ############################################################################
    def __init__(self, length):
        self.can_lie = True
        self.counter = 1
        self.letters_used = []
        self.length = length
        self.letters_left = length
        self.progress = ["█"] * self.letters_left

        self.order = ["e", "a", "r", "i", "o", "t", "n", "s"]
        
        self.fails = []
        
        print(f"{colors.BOLD + colors.BLUE}STAGE ZERO | Current Phrase: " + (" ".join(self.progress)))
        self.make_move(" ", False, "blank")
        print(f"{colors.BOLD + colors.BLUE}STAGE ZERO | Current Phrase: " + (" ".join(self.progress)))
        self.make_move(",", False, "comma")
        print(f"{colors.BOLD + colors.BLUE}STAGE ZERO | Current Phrase: " + (" ".join(self.progress)))
        self.make_move("'", False, "apostrophe")
        print(f"{colors.BOLD + colors.BLUE}STAGE ZERO | Current Phrase: " + (" ".join(self.progress)))
        self.make_move(".", False, "period")
        print(f"{colors.BOLD + colors.BLUE}STAGE ZERO | Current Phrase: " + (" ".join(self.progress)))
        if self.progress[-1] == "█":
            self.make_move("?", False, "question mark")
            print(f"{colors.BOLD + colors.BLUE}STAGE ZERO | Current Phrase: " + (" ".join(self.progress)))
            if self.progress[-1] == "█":
                self.make_move("!", False, "exclamation mark")
                print(f"{colors.BOLD + colors.BLUE}STAGE ZERO | Current Phrase: " + (" ".join(self.progress)))
        
        print(f"{colors.BOLD + colors.BLUE}Entering Stage 1...")
        self.core_game_stage_one()
        
        print(f"{colors.BOLD + colors.BLUE}Entering Stage 2...")
        self.core_game_stage_two()
    
    ############################################################################
    # Runs Stage 1 of the game.                                                #
    # - Guesses letters in order until it is computationally viable to run     #
    #   stage two.                                                             #
    ############################################################################
    def core_game_stage_one(self):
        for letter in self.order:
            self.evaluate_available_words()
            if sum([len(wordlist) for wordlist in self.viable]) < 10000:
                return
            print(f"{colors.BOLD + colors.BLUE}Current Phrase: " + (" ".join(self.progress)))
            self.make_move(letter)
            print(self.words)
    
    ############################################################################
    # Runs Stage 2 of the game.                                                #
    # - Uses individual word entropy combined together to make guesses until   #
    #   it is computationally viable to have lists of entire phrases to run    #
    #   stage three.                                                           #
    ############################################################################
    def core_game_stage_two(self):
        while self.letters_left > 0:
            print(f"{colors.BOLD + colors.BLUE}Current Phrase: " + (" ".join(self.progress)))
            self.evaluate_available_words()
            words = []
            info_list = {}
            total_combinations = 1
            
            for i in range(len(self.viable)):
                # create a unigram probability list
                print(f"{colors.BOLD + colors.YELLOW}STAGE TWO | {self.words[i]} has {len(self.viable[i])} possibilities.")
                p = np.zeros((len(self.viable[i])), dtype=float)
                for j in range(len(self.viable[i])):
                    p[j] = 10 ** getUnigramProb(n, self.viable[i][j])
                # normalize it
                p /= sum(p)
                
                words += self.viable[i]
                # calculate probabilities per letter
                new_list = scripts.calculate(self.words[i], self.viable[i], self.letters_used, p)
                # merge dictionary together
                info_list = {k: info_list.get(k, 0) + new_list.get(k, 0) for k in set(info_list) | set(new_list)}
                
                total_combinations *= len(self.viable[i])
            
            # check for stage 3 viability
            if total_combinations < 2500000:
                # if win, break the loop and finish
                if self.core_game_stage_three():
                    break
                # else continue
                continue         

            # find the best move in stage 2
            max_info_key = max(info_list, key=info_list.get)

            # play the best move
            self.make_move(max_info_key)
                
        print(f"Congrats! You win in {self.counter} moves.")
        
    ############################################################################
    # Runs Stage 3 of the game.                                                #
    # - Bashes all possible combinations of words and retrieves their order 5  #
    #   sentence probabilities. Normalizes the probabilities and only looks at #
    #   the probabilities greater than 0.01. Does the same entropy calculation,#
    #   but based on the entire phrase rather than individual words.           #
    ############################################################################
    def core_game_stage_three(self):
        print(f"{colors.BOLD + colors.BLUE}Entering Stage 3...")
        phrases = []
        
        # generate list of phrases
        gen = self.generatePhrase(0)
        while True:
            try: 
                phrases += [next(gen).strip()]
            except StopIteration:
                break
            
        # remove failed phrases from viability list
        for failed_phrase in self.fails:
            if failed_phrase in phrases:
                phrases.remove(failed_phrase)
            
        # create probability array
        p = np.zeros((len(phrases)), dtype=float)
            
        for i in range(len(phrases)):
            p[i] = 10 ** getSentenceProb(n, phrases[i], len(self.words))
            
        # normalize probabilities
        p /= sum(p)
        
        # cut off anything less than 0.01
        p = np.fromiter((x if x > 0.01 else 0 for x in p), dtype=p.dtype)
        
        # find sorted index
        index = p.argsort()[:][::-1]
        
        # re-normalize with the new truncated array
        p /= sum(p)
        
        # define the new sorted, truncated arrays
        sorted_phrases = np.array(phrases, dtype=str)[index]
        sorted_p = p[index]
        d = {sorted_phrases[i]:sorted_p[i] for i in range(len(sorted_phrases)) if sorted_p[i] > 0}
        
        # format for entropy calculation
        top_phrases = np.array(list(d.keys()), dtype=str)
        top_probs = np.array(list(d.values()), dtype=float)
        
        # calculate phrase entropy
        info_list = scripts.calculate(''.join(self.progress), list(top_phrases), self.letters_used, top_probs)
        
        print(f"{colors.BOLD + colors.BLUE}STAGE THREE | Most likely phrase is {phrases[index[0]]} with probability {p[index[0]]}.")
        
        # if phrase is 98% certain to be correct, guess it
        if p[index[0]] > 0.98:
            phrase = phrases[index[0]]
            i = 0
            while i < len(phrase):
                if phrase[i] == "'":
                    phrase = phrase[:i-1] + phrase[i:]
                    i -= 1
                elif self.progress[i] == ",":
                    phrase = phrase[:i] + "," + phrase[i:]
                    i += 1
                i += 1

            # if there is punctuation, add it
            if len(phrase) + 1 == self.length:
                phrase += self.progress[-1]
            result = input(f"Guess #{self.counter} | Is the phrase '{phrase}'? ")
            # correct guess
            if result == 'Y':
                return True
            # else, incorrect guess, add to failed phrases
            self.fails += [phrases[index[0]]]
            self.counter += 3
            return False
        
        # find top letter choice
        maxInfoKey = max(info_list, key=info_list.get)
        
        # make the best move
        self.make_move(maxInfoKey)
        
        return False
        
    ############################################################################
    # Recursive phrase generator function for Stage 3                          #
    ############################################################################
    def generatePhrase(self, depth, current=''):
        for word in self.viable[depth]:
            if depth == len(self.words) - 1:
                yield current + ' ' + word
            else:
                yield from self.generatePhrase(depth + 1, current + ' ' + word)
        
    ############################################################################
    # Finds all possible words sorted in format of the secret phrase           #
    ############################################################################
    def evaluate_available_words(self):
        viable = []
        for word in self.words:
            viable.append(scripts.getFilteredList(word, VOCAB[str(len(word))], self.letters_used))
        self.viable = viable

    ############################################################################
    # Make the move by prompting the user                                      #
    ############################################################################
    def make_move(self, guess, can_lie=True, custom_name=''):

        print(f'''Letters Guessed: "{'", "'.join(self.letters_used)}"''')
        question = f"Guess #{self.counter}: Is there a {guess}? "
        if custom_name:
            question = f"Guess #{self.counter}: Is there a {custom_name}? "

        # Q1
        answer = input(question).strip()
        self.counter += 1
        
        self.letters_used += [guess]
        
        if answer == 'N':
            # check for lie
            if self.can_lie and can_lie:
                answer_check = input(question).strip()
                self.counter += 1
                # lie has occurred
                if answer_check != answer:
                    self.can_lie = False
                    answer_final = input(question).strip()
                    self.counter += 1
                    # first one is a lie, second one was the truth, so give positions; else, if first was truth, do nothing
                    if answer_check == answer_final: 
                        positions = [int(pos.strip())-1 for pos in answer_check.split(',')[1:]]
                        self.progress_updater(guess, positions)
        elif answer[0] == 'Y':
            positions = [int(pos.strip())-1 for pos in answer.split(',')[1:]]
            
            # if only 1 position, could be a lie; if 2+ positions, cannot be a lie
            if len(positions) == 1 and self.can_lie and can_lie:
                answer_check = input(question).strip()
                self.counter += 1
                # lie has occurred
                if answer_check != answer:
                    self.can_lie = False
                    answer_final = input(question).strip()
                    self.counter += 1
                    # first one is a lie, second one was the truth; else, if first was truth, positions is correct
                    if answer_check == answer_final: 
                        positions = [int(pos.strip())-1 for pos in answer_check.split(',')[1:]]
            
            self.progress_updater(guess, positions)

        # invalid input
        else:
            print(f"{colors.BOLD + colors.RED}Already used or invalid. Try again")
            self.counter -= 1
        self.words = ''.join(self.progress).split(' ')
        i = 0
        while i < len(self.words):
            word = self.words[i]
            if "'" in word:
                self.words[i] = word[:word.index("'")]
                self.words.insert(i+1, word[word.index("'"):])
                i += 1
            if "," in word:
                self.words[i] = word[:-1]
            i += 1
                
        if self.words[-1][-1] in '.?!':
            self.words[-1] = self.words[-1][:-1]
    
    # update the progress left
    def progress_updater(self, guess, positions):
        for pos in positions:
            self.progress[pos] = guess
            self.letters_left -= 1
        return " ".join(self.progress)
    
if __name__ == '__main__':
    
    print(f"{colors.BOLD + colors.BLUE}Welcome to Hangman! Loading data...")
    # Load vocabulary list
    for line in open('vocab.txt').readlines():
        word = line.strip()
        VOCAB[str(len(word))].append(word)

    # Read language model --> set to 1e-5 pruned probabilities at order 5
    readLM(n, "bnc-pruned-3.lm")
    print(f"{colors.BOLD + colors.GREEN}Data loaded!")
    
    # Begin!
    length = int(input(f"How many characters are there in this phrase? ").strip())
    game = Hangman(length)