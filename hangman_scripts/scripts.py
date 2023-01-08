import math

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

def getEntropy(filteredList):
    entropy = 0
    total = 0

    for freq in filteredList:
        entropy -= freq * math.log2(freq)
        total += freq

    entropy /= total
    entropy += math.log2(total)

    return entropy