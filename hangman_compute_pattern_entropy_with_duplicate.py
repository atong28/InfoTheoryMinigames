import numpy as np
from string import ascii_lowercase as alc
import fnmatch
import math

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

print(f"{bcolors.YELLOW+bcolors.BOLD}Loading the wordlist...")

f = open('wikipedia-english-list.txt', 'r', encoding='utf-8')
content = f.read()

# used for parsing
def splitText(entry):
    result = entry.split(" ")
    return (result[0], int(result[1]))

# test if it matches filter. ? = unknown.
def matchesFilter(str, filter, used_letters):
    if len(str) != len(filter): return False
    
    for letter in used_letters:
        if letter in filter: continue
        if letter in str: return False
    
    for i in range(len(str)):
        if filter[i] == "?": 
            if str[i] in used_letters: return False
            continue
        
        if filter[i] != str[i]: return False
        
    return True

# load the wordlist
wordList = list(map(splitText, content.splitlines()))

# take the top 50,000 words as the most likely words
mostLikelyList = wordList[0:50000]

sortedList = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]

sortedLikelyList = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]

# sort the words into their respective lengths
for word in wordList:

    # no words with accents, etc.
    if not word[0].isascii(): continue

    # skip words that are too long (these are usually obscure names of places in europe)
    if len(word[0]) > 39: continue

    sortedList[len(word[0])][word[0]] = word[1]

# sort the words into their respective lengths
for word in mostLikelyList:

    # no words with accents, etc.
    if not word[0].isascii(): continue

    # skip words that are too long (these are usually obscure names of places in europe)
    if len(word[0]) > 39: continue
    
    sortedLikelyList[len(word[0])][word[0]] = word[1]

print(f"{bcolors.GREEN+bcolors.BOLD}Loaded the wordlist.")

def getFilteredList(filter, wordlist, used_letters, printing):
    newFilteredList = {k:v for k,v in wordlist.items() if matchesFilter(k, filter, used_letters)}

    if len(newFilteredList.keys()) == 1:
        if printing: print(f"{bcolors.BLUE+bcolors.BOLD}It must be {list(newFilteredList.keys())[0]}.")
    elif len(newFilteredList.keys()) == 0:
        if printing: print(f"{bcolors.RED+bcolors.BOLD}All options exhausted.")
        return
    
    return newFilteredList

def getEntropy(filteredList):
    entropy = 0
    total = 0

    for v in filteredList.values():
        entropy -= v * math.log2(v)
        total += v

    entropy /= total
    entropy += math.log2(total)

    return entropy

def findBestLetter(filter, wordlist, used_letters):
    
    newFilteredList = getFilteredList(filter, wordlist, used_letters, True)

    # if nothing, just return most likely letter frequencies (TO-DO)
    if not newFilteredList:
        return

    # intialize the dictionary of frequencies
    alphabetList = {}
    entropyList = {}
    infoList = {}

    # calculate the current entropy of all possible items
    currentEntropy = getEntropy(newFilteredList)

    print(f"Current entropy: {currentEntropy} bits.")
    
    # sum up frequencies
    for k, v in newFilteredList.items():
        # iterate through only unique characters
        for letter in k:
            # calculate the filter for that letter
            pattern = ''.join([letter if letter == otherLetter else "?" for otherLetter in k])

            # create the letter if does not exist already
            alphabetList.setdefault(letter, {})

            # add pattern to the letter if does not exist already
            alphabetList[letter].setdefault(pattern, 0)

            # create the letter if does not exist already
            entropyList.setdefault(letter, {})

            # add pattern to the letter if does not exist already
            entropyList[letter].setdefault(pattern, 0)

            # add the frequency value to this pattern to find total.
            alphabetList[letter][pattern] += v

            # initial calculation. need to divide by total and add log of total.
            entropyList[letter][pattern] -= v * math.log2(v)

    # find the entropy from each pattern result for each letter

    # for each pattern, find p log 1/p for p normalized over the totals in that pattern
    # then, resulting entropy of every possible pattern is now calculated. 
    # expected information = current entropy - expected future entropy
    # expected future entropy = probability of no letter * entropy of no letter + probability of letter * expected entropy of all patterns
    # calculate expected information from asking for each letter

    # total of all frequencies for normalization
    allTotals = sum([sum(dictionary.values()) for dictionary in alphabetList.values()])

    for letter, dictionary in alphabetList.items():

        if letter in used_letters: continue

        # add letter to dict if does not exist already, default value is current entropy
        infoList.setdefault(letter, currentEntropy)

        # sum of the totals for the letter
        total = sum(dictionary.values())

        expectedEntropy = 0

        for pattern, freq in dictionary.items():
            entropyList[letter][pattern] /= freq
            entropyList[letter][pattern] += math.log2(freq)

            # subtract the portion of entropy per pattern
            expectedEntropy += freq / total * entropyList[letter][pattern]

        # print(f"Expected resulting entropy if the letter {letter} exists: {expectedEntropy} bits")

        # we've found expected entropy if the letter exists, now we must consider if it does not
        
        temp_used_letters = used_letters + [letter]
        absentFilteredList = getFilteredList(filter, wordlist, temp_used_letters, False)

        expectedAbsentEntropy = 0
        if absentFilteredList:
            expectedAbsentEntropy = getEntropy(absentFilteredList)

        # print(f"Expected resulting entropy if the letter {letter} does not exist: {expectedAbsentEntropy} bits")

        # subtract from information
        infoList[letter] -= expectedEntropy * total / allTotals + expectedAbsentEntropy * (allTotals - total) / allTotals

    # find the maximum information and its corresponding letter
    maxInfo = max(infoList.values())
    maxInfoKey = max(infoList, key=infoList.get)

    # print result
    print(f"{bcolors.RESET}There are {len(newFilteredList.keys())} remaining possible words.")
    print(f"{bcolors.CYAN+bcolors.BOLD}Best letter is {maxInfoKey}: Expected information gained is {maxInfo} bits.")

while True:
    filter = input(f"{bcolors.MAGENTA}Input the filter: ")
    used_letters = input(f"{bcolors.MAGENTA}Input the used letters: ")
    
    if used_letters == '':
        findBestLetter(filter, sortedList[len(filter)], [])
    else:
        findBestLetter(filter, sortedList[len(filter)], [*used_letters])