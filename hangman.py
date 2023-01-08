from hangman_scripts import colors, scripts
from collections import defaultdict
import numpy as np
from srilm import *
import pprint

def step(mu_prev: np.ndarray,
         emission_probs: np.ndarray,
         transition_probs: np.ndarray,
         observed_state: int) -> tuple[np.ndarray, np.ndarray]:
    """Runs one step of the Viterbi algorithm.
    
    Args:
        mu_prev: probability distribution with shape (num_hidden),
            the previous mu
        emission_probs: the emission probability matrix (num_hidden,
            num_observed)
        transition_probs: the transition probability matrix, with
            shape (num_hidden, num_hidden)
        observed_state: the observed state at the current step
    
    Returns:
        - the mu for the next step
        - the maximizing previous state, before the current state,
          as an int array with shape (num_hidden)
    """
    
    pre_max = mu_prev * transition_probs.T
    max_prev_states = np.argmax(pre_max, axis=1)
    max_vals = pre_max[np.arange(len(max_prev_states)), max_prev_states]
    mu_new = max_vals * emission_probs[:, observed_state]
    
    return mu_new, max_prev_states


def viterbi(emission_probs: np.ndarray,
            transition_probs: np.ndarray,
            start_probs: np.ndarray,
            observed_states: list[int]) -> tuple[list[int], float]:
    """Runs the Viterbi algorithm to get the most likely state sequence.
    
    Args:
        emission_probs: the emission probability matrix (num_hidden,
            num_observed)
        transition_probs: the transition probability matrix, with
            shape (num_hidden, num_hidden)
        start_probs: the initial probabilies for each state, with shape
            (num_hidden)
        observed_states: the observed states at each step
    
    Returns:
        - the most likely series of states
        - the joint probability of that series of states and the observed
    """
    
    # Runs the forward pass, storing the most likely previous state.
    mu = start_probs * emission_probs[:, observed_states[0]]
    all_prev_states = []
    for observed_state in observed_states[1:]:
        mu, prevs = step(mu, emission_probs, transition_probs, observed_state)
        all_prev_states.append(prevs)
    
    # Traces backwards to get the maximum likelihood sequence.
    state = np.argmax(mu)
    sequence_prob = mu[state]
    state_sequence = [state]
    for prev_states in all_prev_states[::-1]:
        state = prev_states[state]
        state_sequence.append(state)
    
    return state_sequence[::-1], sequence_prob

VOCAB = defaultdict(lambda: [])
np.set_printoptions(precision=3)
n = initLM(2)

class Hangman():

    def __init__(self, secret):
        self.secret = secret
        self.counter = 1
        self.letters_used = []
        
        self.letters_left = len(self.secret)
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
            emission_matrix = np.zeros((sum([len(wordlist) for wordlist in self.viable]), len(self.viable)))
            
            info_list = {}
            
            total_combinations = 1
            
            for i in range(len(self.viable)):
                # create a unigram probability list
                p = np.zeros((len(self.viable[i])), dtype=float)
                for j in range(len(self.viable[i])):
                    p[j] = 10 ** getUnigramProb(n, self.viable[i][j])
                p /= sum(p)
                
                
                e = scripts.getEntropy(p)
                print(f"{colors.BOLD + colors.YELLOW}STAGE TWO | {self.words[i]} has {len(self.viable[i])} possibilities.")
                print(f"{colors.BOLD + colors.YELLOW}STAGE TWO | {self.words[i]} has an entropy of {e} bits.")
                emission_matrix[len(words):len(words)+len(self.viable[i]), i] = 1
                words += self.viable[i]
                
                new_list = scripts.calculate(self.words[i], self.viable[i], self.letters_used, p)
                info_list = {k: info_list.get(k, 0) + new_list.get(k, 0) for k in set(info_list) | set(new_list)}
                
                total_combinations *= len(self.viable[i])
            
            if total_combinations < 2500000:
                phrase, prob = self.core_game_stage_three()
                if prob > 0.95:
                    print(f"STAGE THREE | Guessing phrase {phrase}")
                    break
                continue
            
            initial_prob = np.zeros((len(words)), dtype=float)
            for i in range(len(self.viable[0])):
                initial_prob[i] = 10 ** getBigramProb(n, f'<s> {self.viable[0][i]}')
            initial_prob /= sum(initial_prob)
            
            
            # define the transition matrix
            transition_matrix = np.zeros((len(words), len(words)), dtype=float)
            buf = 0
            for i in range(len(self.viable)-1):
                for j in range(len(self.viable[i])):
                    for k in range(len(self.viable[i+1])):
                        transition_matrix[buf+j, buf+k+len(self.viable[i])] = 10 ** getBigramProb(n, ' '.join([self.viable[i][j], self.viable[i+1][k]]))
                    # normalize probabilities
                    transition_matrix[buf+j] /= sum(transition_matrix[buf+j])
                buf += len(self.viable[i])
            
            sequence, prob = viterbi(emission_matrix, transition_matrix, initial_prob, list(range(len(self.viable))))
            
            
            seq = []
            for result in sequence:
                seq += [words[result]]
            print(f"{colors.BOLD + colors.BLUE}STAGE TWO | Most Likely Sequence: {' '.join(seq)}")
            print(f"{colors.BOLD + colors.BLUE}STAGE TWO | Probability: {prob}")
            
            if prob > 0.95:
                print(f"Guessing phrase {' '.join(seq)}")
                break
            
            sort = dict(sorted(info_list.items(), key=lambda item: item[1]))
            for i in reversed(range(len(sort.values()))):
                k = list(sort.keys())
                # find the highest entropy as long as it is in the markov model
                if k[i] in ''.join(seq):
                    print(f"{colors.CYAN+colors.BOLD}Best letter is {k[i]}: Expected information gained is {sort[k[i]]} bits.")
                    self.make_move()#k[i])
                    break
            
            
            
                
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
        
        searchDepth = (-1) * min(500, len(phrases))
        
        index = p.argsort()[searchDepth:][::-1]
        
        topPhrases = np.array(phrases, dtype=str)[index]
        
        info_list = scripts.calculate(''.join(self.progress), list(topPhrases), self.letters_used, p)
        
        for i in range(min(20,len(index))):
            print(f"{colors.BOLD + colors.BLUE}STAGE THREE | Likely phrase #{i+1} is {phrases[index[i]]} with probability {p[index[i]]}")
            
        maxInfo = max(info_list.values())
        maxInfoKey = max(info_list, key=info_list.get)
        
        print(f"{colors.CYAN+colors.BOLD}Best letter is {maxInfoKey}: Expected information gained is {maxInfo} bits.")
        
        self.make_move()
        
        return phrases[index[0]], p[index[0]]
        
        
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

    def make_move(self, guess=""):

        if not guess:
            guess = input("Guess a letter -> ").lower()
        self.counter += 1
        
        # correct guess
        if guess in self.secret and guess not in self.letters_used:
            self.letters_used += [guess]
            print(f"{colors.BOLD + colors.BLUE}Progress: {self.progress_updater(guess)}")
            print(f"{colors.BOLD + colors.YELLOW}Letters used: "+ (", ".join(self.letters_used)))
            
        # incorrect guess
        elif guess not in self.secret and guess not in self.letters_used:
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
    
    print(f"{colors.BOLD + colors.BLUE}Welcome to Hangman! Loading data...")
    for line in open('vocabStrict.txt').readlines():
        word = line.strip()
        VOCAB[str(len(word))].append(word)

    readLM(n, "bnc-pruned-2.lm")
    print(f"{colors.BOLD + colors.GREEN}Data loaded!")
    secret = input("What is the secret? Enter here: ")
    game = Hangman(secret.lower())