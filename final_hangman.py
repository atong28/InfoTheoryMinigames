from hangman_scripts import colors, scripts
from collections import defaultdict
import numpy as np
from srilm import *

VOCAB = defaultdict(lambda: [])
np.set_printoptions(precision=3)
n = initLM(5)

class Hangman():

    def __init__(self, length):
        self.can_lie = True
        self.counter = 1
        self.letters_used = []
        
        self.letters_left = length
        self.progress = ["█"] * self.letters_left

        self.order = ["e", "a", "r", "i", "o", "t", "n", "s"]
        
        self.make_move(" ")
        
        self.core_game_stage_one()
        
        self.core_game_stage_two()
    
    def core_game_stage_one(self):
        for letter in self.order:
            self.evaluate_available_words()
            if sum([len(wordlist) for wordlist in self.viable]) < 5000:
                print(f"{colors.BOLD + colors.GREEN}Stage 1 completed. Moving on to stage 2...")
                return
            print(f"{colors.BOLD + colors.BLUE}STAGE ONE | Current Phrase: " + (" ".join(self.progress)))
            self.make_move(letter)
    
    def core_game_stage_two(self):
        print(f"{colors.BOLD + colors.BLUE}STAGE TWO | Current Phrase: " + (" ".join(self.progress)))
        
        while self.letters_left > 0:
            print(f"{colors.BOLD + colors.BLUE}STAGE TWO | Analyzing state...")
            self.evaluate_available_words()
            print(f"{colors.BOLD + colors.BLUE}STAGE TWO | Number of possibilities for each word:")
            words = []
            
            info_list = {}
            
            total_combinations = 1
            
            for i in range(len(self.viable)):
                # create a unigram probability list
                p = np.zeros((len(self.viable[i])), dtype=float)
                for j in range(len(self.viable[i])):
                    p[j] = 10 ** getUnigramProb(n, self.viable[i][j])
                p /= sum(p)
                
                print(f"{colors.BOLD + colors.YELLOW}STAGE TWO | {self.words[i]} has {len(self.viable[i])} possibilities.")
                words += self.viable[i]
                
                new_list = scripts.calculate(self.words[i], self.viable[i], self.letters_used, p)
                info_list = {k: info_list.get(k, 0) + new_list.get(k, 0) for k in set(info_list) | set(new_list)}
                
                total_combinations *= len(self.viable[i])
            
            if total_combinations < 2500000:
                if self.core_game_stage_three():
                    break
                continue         
            
            max_info = max(info_list.values())
            max_info_key = max(info_list, key=info_list.get)

            # print result
            print(f"{colors.CYAN+colors.BOLD}Best letter is {max_info_key}: Expected information gained is {max_info} bits.")
            self.make_move(max_info_key)
                
        print(f"Congrats! You win in {self.counter} moves.")
        
    def core_game_stage_three(self):
        phrases = []
        gen = self.generatePhrase(0)
        while True:
            try: 
                phrases += [next(gen).strip()]
            except StopIteration:
                break
            
        p = np.zeros((len(phrases)), dtype=float)
            
        for i in range(len(phrases)):
            p[i] = 10 ** getSentenceProb(n, phrases[i], len(self.words))
            
        p /= sum(p)
        
        p = np.fromiter((x if x > 0.01 else 0 for x in p), dtype=p.dtype)
        
        index = p.argsort()[:][::-1]
        
        p /= sum(p)
        
        sorted_phrases = np.array(phrases, dtype=str)[index]
        
        sorted_p = p[index]
        
        d = {sorted_phrases[i]:sorted_p[i] for i in range(len(sorted_phrases)) if sorted_p[i] > 0}
        
        top_phrases = np.array(list(d.keys()), dtype=str)
        
        top_probs = np.array(list(d.values()), dtype=float)
        
        info_list = scripts.calculate(''.join(self.progress), list(top_phrases), self.letters_used, top_probs)
        
        for i in range(min(10,len(index))):
            print(f"{colors.BOLD + colors.BLUE}STAGE THREE | Likely phrase #{i+1} is {phrases[index[i]]} with probability {p[index[i]]}")
            
        maxInfo = max(info_list.values())
        maxInfoKey = max(info_list, key=info_list.get)
        
        print(f"{colors.CYAN+colors.BOLD}STAGE THREE | Best letter is {maxInfoKey}: Expected information gained is {maxInfo} bits.")
        
        if p[index[0]] > 0.95:
            print(f"STAGE THREE | Guessing phrase {phrases[index[0]]}")
            return True
        
        self.make_move(maxInfoKey)
        
        return False
        
        
    def generatePhrase(self, depth, current=''):
        for word in self.viable[depth]:
            if depth == len(self.words) - 1:
                yield current + ' ' + word
            else:
                yield from self.generatePhrase(depth + 1, current + ' ' + word)
        

    def evaluate_available_words(self):
        viable = []
        for word in self.words:
            viable.append(scripts.getFilteredList(word, VOCAB[str(len(word))], self.letters_used))
        self.viable = viable

    def make_move(self, guess, can_lie=True):

        answer = input(f"Guess #{self.counter}: Is there a {guess}?").strip()
        self.counter += 1
        
        self.letters_used += [guess]
        
        if answer == 'N':
            if self.can_lie and can_lie:
                answer_check = input(f"Guess #{self.counter}: Is there a {guess}?").strip()
                self.counter += 1
                # lie has occurred
                if answer_check != answer:
                    self.can_lie = False
                    answer_final = input(f"Guess #{self.counter}: Is there a {guess}?").strip()
                    self.counter += 1
                    # first one is a lie, second one was the truth, so give positions; else, if first was truth, do nothing
                    if answer_check == answer_final: 
                        positions = [int(pos.strip()) for pos in answer_check.split(',')[1:]]
                        self.progress_updater(guess, positions)
        elif answer[0] == 'Y':
            positions = [int(pos.strip()) for pos in answer.split(',')[1:]]
            
            # if only 1 position, could be a lie; if 2+ positions, cannot be a lie
            if len(positions) == 1 and self.can_lie and can_lie:
                answer_check = input(f"Guess #{self.counter}: Is there a {guess}?").strip()
                self.counter += 1
                # lie has occurred
                if answer_check != answer:
                    self.can_lie = False
                    answer_final = input(f"Guess #{self.counter}: Is there a {guess}?").strip()
                    self.counter += 1
                    # first one is a lie, second one was the truth; else, if first was truth, positions is correct
                    if answer_check == answer_final: 
                        positions = [int(pos.strip()) for pos in answer_check.split(',')[1:]]
            
            self.progress_updater(guess, positions)

        # invalid input
        else:
            print(f"{colors.BOLD + colors.RED}Already used or invalid. Try again")
            self.counter -= 1

        self.words = "".join(self.progress).split(" ")
    
    # update the progress left
    def progress_updater(self, guess, positions):
        for pos in positions:
            self.progress[pos] = guess
            self.letters_left -= 1
        return " ".join(self.progress)
    
    

if __name__ == '__main__':
    
    print(f"{colors.BOLD + colors.BLUE}Welcome to Hangman! Loading data...")
    for line in open('vocab.txt').readlines():
        word = line.strip()
        VOCAB[str(len(word))].append(word)

    readLM(n, "bnc-pruned-3.lm")
    print(f"{colors.BOLD + colors.GREEN}Data loaded!")
    length = int(input(f"How many characters are there in this phrase? ").strip())
    game = Hangman(length)