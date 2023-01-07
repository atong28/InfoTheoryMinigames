from hangman_scripts import colors
from collections import defaultdict
import numpy as np
from srilm import *

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
    newFilteredList = [word for word in wordlist if matchesFilter(word, filter, used_letters)]

    if len(newFilteredList) == 0:
        return []
    
    return newFilteredList

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

n = initLM(2)

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
        emission_matrix = np.zeros((sum([len(wordlist) for wordlist in viable]), len(viable)))
        for i in range(len(viable)):
            print(f"{self.words[i]} has {len(viable[i])} possibilities.")
            print(viable[i])
            emission_matrix[len(words):len(words)+len(viable[i]), i] = 1
            words += viable[i]
            

        # if too many possibilities, ask another letter
        
        initial_prob = [10 ** getBigramProb(n, f"<s> {word}") for word in words]
        total = sum(initial_prob)
        initial_prob = [norm/total for norm in initial_prob]
        transition_matrix = np.zeros((len(words), len(words)), dtype=float)
        
        print(f"Total number of words: {len(words)}")
        print(f"Size of array Pi: {len(initial_prob)}")
        print(initial_prob)
        print(f"Shape of matrix Tm: {transition_matrix.shape}")
        print(transition_matrix)
        print(f"Shape of matrix Em: {emission_matrix.shape}")
        print(emission_matrix)
        
        buf = 0
        for i in range(len(viable)-1):
            for j in range(len(viable[i])):
                for k in range(len(viable[i+1])):
                    print("Checking: "+' '.join([viable[i][j], viable[i+1][k]]) + f" | {getBigramProb(n, ' '.join([viable[i][j], viable[i+1][k]]))}")
                    print(f"Updating location at {buf+j}, {buf+j+k}")
                    transition_matrix[buf+j, buf+j+k] = 10 ** getBigramProb(n, ' '.join([viable[i][j], viable[i+1][k]]))
                # normalize probabilities
                transition_matrix[buf+j] /= sum(transition_matrix[buf+j])
            buf += len(viable[i])
            
        sequence, prob = viterbi(emission_matrix, transition_matrix, initial_prob, list(range(len(viable))))
        
        print(f"Most Likely Sequence: {sequence}")
        for result in sequence:
            print(words[result])
        print(f"Probability: {prob}")

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
    
    print(f"{colors.BOLD + colors.BLUE}Welcome to Hangman! Loading data...")
    for line in open('vocabStricter.txt').readlines():
        word = line.strip()
        VOCAB[str(len(word))].append(word)

    readLM(n, "bnc-pruned.lm")
    print(f"{colors.BOLD + colors.GREEN}Data loaded!")
    secret = input("What is the secret? Enter here: ")
    game = Hangman(secret.lower())