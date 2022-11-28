import os
import json
from string import ascii_lowercase as alc
from collections import defaultdict
from lib.scripts import matchesFilter, getFilteredList, getEntropy

MAX_RECURSION_DEPTH = 5

def updateFilter(filter, word, letter):
    filterList = list(filter)
    for i in range(len(filter)):
        if filter[i] == '?' and word[i] == letter:
            filterList[i] = letter
    return ''.join(filterList)

def calculate(filter, wordlist, used_letters):

    if '?' not in filter: return

    if len(wordlist) == 1:
        pass

    if len(used_letters) == MAX_RECURSION_DEPTH:
        return getEntropy(wordlist)

    letterDict = defaultdict(lambda: defaultdict(lambda: {'freq':0, 'next':{}}))

    for word, freq in wordlist.items():
        
        for letter in set(word):
            
            if letter in used_letters: continue

            # create pattern
            pattern = updateFilter(filter, word, letter)

            # add the frequency value to this pattern to find total.
            letterDict[letter][pattern]['freq'] += freq

    # next, iterate through all possible patterns and compute recursively
    for letter, patternDict in letterDict.items():
        for pattern in patternDict.keys():
            newWordlist = getFilteredList(pattern, wordlist, used_letters + [letter], False)
            letterDict[letter][pattern]['next'] = calculate(pattern, newWordlist, used_letters + [letter])

    return letterDict

if __name__ == "__main__":
    f = open(os.path.abspath('wikipedia-english-list-cleaned.json'), 'r')

    wordlist = json.load(f)

    computedDict = defaultdict(lambda: {})

    for length, wordDict in wordlist.items():
        print(f"Evaluating length {length}")
        computedDict = calculate('?'*int(length), wordlist[length], [])
        with open(f'wikipedia-precomputed-{length}.json', 'w') as f:
            json.dump(computedDict, f, indent=4)