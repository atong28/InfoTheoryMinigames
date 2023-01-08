import math
from collections import defaultdict
import numpy as np

def matchesFilter(str, filter, used_letters):
    if len(str) != len(filter): return False
    
    for letter in used_letters:
        if letter in filter: continue
        if letter in str: return False
    
    for i in range(len(str)):
        if filter[i] == "█": 
            if str[i] in used_letters: return False
            continue
        
        if filter[i] != str[i]: return False
    return True

def getFilteredList(filter, wordlist, used_letters):
    newFilteredList = [word for word in wordlist if matchesFilter(word, filter, used_letters)]

    if len(newFilteredList) == 0:
        return []
    
    return newFilteredList

def getEntropy(filtered_list):
    entropy = 0
    total = 0

    for freq in filtered_list:
        if freq != 0:
            entropy -= freq * math.log2(freq)
            total += freq

    entropy /= total
    entropy += math.log2(total)

    return entropy

def calculate(filter, wordlist, used_letters, p):

    # calculate the current entropy of all possible items
    currentEntropy = getEntropy(p)

    alphabetList = defaultdict(lambda: defaultdict(lambda: 0))
    entropyList = defaultdict(lambda: defaultdict(lambda: 0))
    infoList = defaultdict(lambda: currentEntropy)

    print(f"Current entropy: {currentEntropy} bits.")
    
    # sum up frequencies
    for i in range(len(wordlist)):
        
        k = wordlist[i]
        v = p[i]
        # iterate through only unique characters
        for letter in set(k):
            # calculate the filter for that letter
            pattern = ''.join([letter if letter == otherLetter else "█" for otherLetter in k])

            # add the frequency value to this pattern to find total.
            alphabetList[letter][pattern] += v

            # initial calculation. need to divide by total and add log of total.
            entropyList[letter][pattern] -= v * math.log2(v)

    # total of all frequencies for normalization
    all_totals = sum([sum(dictionary.values()) for dictionary in alphabetList.values()])

    for letter, dictionary in alphabetList.items():

        if letter in used_letters: continue

        # sum of the totals for the letter
        total = sum(dictionary.values())

        expected_present_entropy = 0

        for pattern, freq in dictionary.items():

            # completes the entropy calculation.
            entropyList[letter][pattern] /= freq
            entropyList[letter][pattern] += math.log2(freq)
            expected_present_entropy += freq / total * entropyList[letter][pattern]

        # we've found expected entropy if the letter exists, now we must consider if it does not
        temp_used_letters = used_letters + [letter]
        absent_filtered_list = getFilteredList(filter, wordlist, temp_used_letters)
        ap = np.zeros((len(absent_filtered_list)), dtype=float)
        
        count = 0
        for i in range(len(wordlist)):
            if wordlist[i] in absent_filtered_list:
                ap[count] = p[i]
                count += 1
        ap /= sum(ap)

        expected_absent_entropy = 0
        if absent_filtered_list:
            expected_absent_entropy = getEntropy(ap)

        print(f"For letter {letter}, PE = {expected_present_entropy}, AE = {expected_absent_entropy}")

        # set the values for expected information gained
        infoList[letter] -= expected_present_entropy * total / all_totals + expected_absent_entropy * (all_totals - total) / all_totals

    return infoList