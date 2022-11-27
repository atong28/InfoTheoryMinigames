import numpy as np
from string import ascii_lowercase as alc
import fnmatch

f = open('wikipedia-english-list.txt', 'r', encoding='utf-8')
content = f.read()

def splitText(entry):
    result = entry.split(" ")
    return (result[0], int(result[1]))

def matchesFilter(str, filter, used_letters):
    if len(str) != len(filter): return False
    
    for letter in used_letters:
        if letter in filter: continue
        if letter in str: return False
    
    for i in range(len(str)):
        if filter[i] == "?": continue
        if filter[i] != str[i]: return False
    return True

wordList = list(map(splitText, content.splitlines()))

sortedList = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]

for word in wordList:
    if not word[0].isascii(): continue
    if len(word[0]) > 39: continue
    sortedList[len(word[0])][word[0]] = word[1]

print("Loaded the wordlist.")

def findBestLetter(filter, wordlist, used_letters):
    
    print(f"Finding best letter with filter {filter}, used letters {used_letters}")
    
    newFilteredList = {k:v for k,v in wordlist.items() if matchesFilter(k, filter, used_letters)}

    # intialize the dictionary of frequencies
    alphabetList = {'-':0, "'":0, "_":0}
    for letter in alc:
        alphabetList[letter] = 0
    
    # sum up frequencies
    for k, v in newFilteredList.items():
        for letter in [*k]:
            alphabetList[letter] += v

    # normalize it and find the one closest to 0.5
    total = sum(alphabetList.values())
    frequencies = {k: v * 4 / total for k, v in alphabetList.items()}

    # remove letters already used
    for letter in used_letters:
        frequencies[letter] = 0

    print(frequencies)

    normalized = [abs(v - 0.5) for v in frequencies.values()]

    i = normalized.index(min(normalized))

    # print result
    print(f"Remaining wordlist: {newFilteredList.keys()}")
    print(f"Best letter is at index {i}: {list(frequencies.keys())[i]} at frequency {list(frequencies.values())[i]}")

while True:
    filter = input("Input the filter: ")
    used_letters = input("Input the used letters: ")
    
    if used_letters == '':
        findBestLetter(filter, sortedList[len(filter)], [])
    else:
        findBestLetter(filter, sortedList[len(filter)], [*used_letters])