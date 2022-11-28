import math
from collections import defaultdict
from lib.getWordlist import *
import lib.colors as bcolors
from lib.scripts import getFilteredList, getEntropy

def findBestLetter(filter, wordlist, used_letters):
    
    newFilteredList = getFilteredList(filter, wordlist, used_letters, True)

    # if nothing, just return most likely letter frequencies (TO-DO)
    if not newFilteredList:
        return

    # calculate the current entropy of all possible items
    currentEntropy = getEntropy(newFilteredList)

    alphabetList = defaultdict(lambda: defaultdict(lambda: 0))
    entropyList = defaultdict(lambda: defaultdict(lambda: 0))
    infoList = defaultdict(lambda: currentEntropy)

    print(f"Current entropy: {currentEntropy} bits.")
    
    # sum up frequencies
    for k, v in newFilteredList.items():
        # iterate through only unique characters
        for letter in ''.join(set(k)):
            # calculate the filter for that letter
            pattern = ''.join([letter if letter == otherLetter else "?" for otherLetter in k])

            # add the frequency value to this pattern to find total.
            alphabetList[letter][pattern] += v

            # initial calculation. need to divide by total and add log of total.
            entropyList[letter][pattern] -= v * math.log2(v)

    # total of all frequencies for normalization
    allTotals = sum([sum(dictionary.values()) for dictionary in alphabetList.values()])

    for letter, dictionary in alphabetList.items():

        if letter in used_letters: continue

        # sum of the totals for the letter
        total = sum(dictionary.values())

        expectedPresentEntropy = 0

        for pattern, freq in dictionary.items():

            # completes the entropy calculation.
            entropyList[letter][pattern] /= freq
            entropyList[letter][pattern] += math.log2(freq)
            expectedPresentEntropy += freq / total * entropyList[letter][pattern]

        # we've found expected entropy if the letter exists, now we must consider if it does not
        temp_used_letters = used_letters + [letter]
        absentFilteredList = getFilteredList(filter, wordlist, temp_used_letters, False)

        expectedAbsentEntropy = 0
        if absentFilteredList:
            expectedAbsentEntropy = getEntropy(absentFilteredList)

        # subtract from information
        infoList[letter] -= expectedPresentEntropy * total / allTotals + expectedAbsentEntropy * (allTotals - total) / allTotals

    # find the maximum information and its corresponding letter
    maxInfo = max(infoList.values())
    maxInfoKey = max(infoList, key=infoList.get)

    # print result
    print(f"{bcolors.RESET}There are {len(newFilteredList.keys())} remaining possible words.")
    print(f"{bcolors.CYAN+bcolors.BOLD}Best letter is {maxInfoKey}: Expected information gained is {maxInfo} bits.")

if __name__ == '__main__':

    sortedList = importList()
    while True:

        filter = input(f"{bcolors.MAGENTA}Input the filter: ")
        used_letters = input(f"{bcolors.MAGENTA}Input the used letters: ")
        
        if used_letters == '':
            findBestLetter(filter, sortedList[len(filter)], [])
        else:
            findBestLetter(filter, sortedList[len(filter)], [*used_letters])