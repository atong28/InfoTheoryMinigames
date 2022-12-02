from srilm import *
import time

# Initialize a trigram LM variable (1 = unigram, 2 = bigram and so on)
n = initLM(5)

print("Reading language model...")
timer = time.perf_counter()
readLM(n, "bnc-pruned.lm")
timerEnd = time.perf_counter()
print(f"Read language model in {timerEnd - timer:0.3f}s.")

print(f"There are {howManyNgrams(n, 1)} unigrams in this LM")
print(f"There are {howManyNgrams(n, 2)} bigrams in this LM")
print(f"There are {howManyNgrams(n, 3)} trigrams in this LM")
print(f"There are {howManyNgrams(n, 4)} 4-grams in this LM")
print(f"There are {howManyNgrams(n, 5)} 5-grams in this LM")

# Query the LM to get the final log probability for an entire sentence.
# Note that this is  different from a n-gram probability because
  # (1) For a sentence, SRILM appends <s> and </s> to its beginning
  #     and the end respectively
  # (2) The log prob of a probability is the sum of all individual
  #     n-gram log probabilities
print("3. Sentence log probabilities and perplexities:")
sprob = getSentenceProb(n,'there are some good',4)
print("   p('there are some good') = {}".format(sprob))

# the perplexity
sppl = getSentencePpl(n,'there are some good', 4)
print("   ppl('there are some good') = {}".format(sppl))



# Free LM variable
deleteLM(n)
