from srilm import *

n = initLM(5)

readLM(n, "bnc-pruned.lm")

p1 = getUnigramProb(n, '<s>')

p2 = getBigramProb(n, '<s> hello')

print(f"{p2}/{p1} = {p2/p1}")

