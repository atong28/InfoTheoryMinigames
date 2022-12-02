import os
f = open(os.path.abspath('bnc-pruned.lm'), 'r', encoding='utf-8')
content = f.read().splitlines()

index1 = content.index('\\2-grams:') + 1
index2 = content.index('\\3-grams:') - 1

unigrams = content[index1:index2]

sumProb = 0

for entry in unigrams:
    split = entry.split()
    sumProb += 10 ** eval(split[0]) 

print(sumProb)