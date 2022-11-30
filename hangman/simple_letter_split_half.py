from string import ascii_lowercase as alc
from collections import defaultdict
from lib.getWordlist import *
import lib.colors as bcolors
from lib.scripts import getFilteredList



def findBestLetter(filter, wordlist, used_letters):
    
    newFilteredList = getFilteredList(filter, wordlist, used_letters, True)

    # intialize the dictionary of frequencies
    alphabetList = defaultdict(lambda: 0)
    
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
    print(newFilteredList)
    print(f"{bcolors.CYAN+bcolors.BOLD}Best letter is at index {i}: {list(frequencies.keys())[i]} at frequency {list(frequencies.values())[i]}")

if __name__ == '__main__':

    sortedList = importList()

    while True:
        filter = input(f"{bcolors.MAGENTA}Input the filter: ")
        used_letters = input(f"{bcolors.MAGENTA}Input the used letters: ")
        
        if used_letters == '':
            findBestLetter(filter, sortedList[len(filter)], [])
        else:
            findBestLetter(filter, sortedList[len(filter)], [*used_letters])