import numpy as np
from string import ascii_lowercase as alc
import fnmatch

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

def findBestLetter(filter, wordlist, secondary_wordlist, used_letters):
    
    print(f"{bcolors.RESET}Finding best letter with filter {filter}, used letters {used_letters}")
    
    newFilteredList = {k:v for k,v in wordlist.items() if matchesFilter(k, filter, used_letters)}
    newSecondaryFilteredList = {k:v for k,v in secondary_wordlist.items() if matchesFilter(k, filter, used_letters)}

    if len(newFilteredList.keys()) == 1:
        print(f"{bcolors.BLUE+bcolors.BOLD}Most likely to be {list(newFilteredList.keys())[0]}. Checking alternate dictionary:")
        newFilteredList = newSecondaryFilteredList
    elif len(newFilteredList.keys()) == 0:
        if len(newSecondaryFilteredList.keys()) == 1:
            print(f"{bcolors.BLUE+bcolors.BOLD}Most likely to be {list(newSecondaryFilteredList.keys())[0]}.")
            return
        print(f"{bcolors.RED+bcolors.BOLD}Likely options exhausted; moving on to secondary dictionary.")
        newFilteredList = newSecondaryFilteredList
    else:
        print(f"{bcolors.GREEN+bcolors.BOLD}Proceeding with regular dictionary.")

    # intialize the dictionary of frequencies
    alphabetList = {'-':0, "'":0, "_":0}
    for letter in alc:
        alphabetList[letter] = 0
    
    # sum up frequencies
    for k, v in newFilteredList.items():
        for letter in [*k]:
            alphabetList[letter] += v

    # remove letters already used
    for letter in used_letters:
        alphabetList[letter] = 0

    # normalize it and find the one closest to 0.5
    total = sum(alphabetList.values())
    frequencies = {k: v * filter.count("?") / total for k, v in alphabetList.items()}

    

    counter = 0
    print(f"{bcolors.YELLOW+bcolors.BOLD}Resulting letter frequencies:")
    freqString = ""
    for k, v in frequencies.items():
        freqString += f'{bcolors.RESET}| {bcolors.YELLOW+bcolors.BOLD+k}: {bcolors.RESET+str(round(v, 3)).ljust(5)} '
        counter += 1
        if counter % 4 == 0: freqString += '|\n'
    print(freqString)

    normalized = [abs(v - 0.5) for v in frequencies.values()]

    i = normalized.index(min(normalized))

    # print result
    print(f"{bcolors.RESET}There are {len(newFilteredList.keys())} remaining possible words")
    print(f"{bcolors.CYAN+bcolors.BOLD}Best letter is at index {i}: {list(frequencies.keys())[i]} at frequency {list(frequencies.values())[i]}")

while True:
    filter = input(f"{bcolors.MAGENTA}Input the filter: ")
    used_letters = input(f"{bcolors.MAGENTA}Input the used letters: ")
    
    if used_letters == '':
        findBestLetter(filter, sortedLikelyList[len(filter)], sortedList[len(filter)], [])
    else:
        findBestLetter(filter, sortedLikelyList[len(filter)], sortedList[len(filter)], [*used_letters])