from collections import defaultdict
import lib.colors as bcolors
from string import ascii_lowercase as alc
import os

def splitText(entry):
    result = entry.split(" ")
    return (result[0], int(result[1]))

def isWord(word):
    for letter in alc:
        if letter in word:
            return True
    return False

def importList():

    print(f"{bcolors.YELLOW+bcolors.BOLD}Loading the wordlist...")

    f = open(os.path.abspath('wikipedia-english-list.txt'), 'r', encoding='utf-8')
    content = f.read()

    # load the wordlist
    wordList = list(map(splitText, content.splitlines()))
    sortedList = defaultdict(lambda: {})

    # sort the words into their respective lengths
    for word in wordList:

        # no words with accents, etc.
        if not word[0].isascii(): continue

        if not isWord(word[0]): continue

        sortedList[len(word[0])][word[0]] = word[1]

    print(f"{bcolors.GREEN+bcolors.BOLD}Loaded the wordlist.")

    return sortedList