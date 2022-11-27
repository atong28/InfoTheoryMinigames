import numpy as np
from string import ascii_lowercase as alc
import fnmatch

f = open('top50k.txt', 'r', encoding='utf-8')
content = f.read()

def splitText(entry):
    result = entry.split(" ")
    return (result[0], int(result[1]))

def matchesFilter(str, filter):
    if len(str) != len(filter): return False
    for i in range(len(str)):
        if filter[i] == "?": continue
        if filter[i] != str[i]: return False
    return True

wordList = list(map(splitText, content.splitlines()))

sortedList = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]

for word in wordList:
    if not word[0].isascii(): continue
    if len(word[0]) > 39: print(word)
    sortedList[len(word[0])][word[0]] = word[1]

def findBestLetter(filter, wordlist):
    newFilteredList = {k:v for k,v in wordlist.items() if matchesFilter(k, filter)}

    # intialize the dictionary of frequencies
    alphabetList = {'-':0, "'":0}
    for letter in alc:
        alphabetList[letter] = 0
    
    # sum up frequencies
    for k, v in newFilteredList.items():
        for letter in [*k]:
            alphabetList[letter] += v

    # normalize it and find the one closest to 0.5
    total = sum(alphabetList.values())
    frequencies = {k: v * 4 / total for k, v in alphabetList.items()}

    normalized = [abs(v - 0.5) for v in frequencies.values()]

    i = normalized.index(min(normalized))

    # print result
    print(f"Remaining wordlist: {newFilteredList.keys()}")
    print(f"Best letter is at index {i}: {list(frequencies.keys())[i]} at frequency {list(frequencies.values())[i]}")

while True:
    filter = input("Input the filter: ")
    length = int(input("Input the length of the word: "))
    findBestLetter(filter, sortedList[length])