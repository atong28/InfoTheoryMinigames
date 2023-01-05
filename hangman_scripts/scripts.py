import colors as bcolors

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

def getFilteredList(filter, wordlist, used_letters, printing):
    newFilteredList = {k:v for k,v in wordlist.items() if matchesFilter(k, filter, used_letters)}

    if len(newFilteredList.keys()) == 1:
        if printing: print(f"{bcolors.BLUE+bcolors.BOLD}It must be {list(newFilteredList.keys())[0]}.")
    elif len(newFilteredList.keys()) == 0:
        if printing: print(f"{bcolors.RED+bcolors.BOLD}All options exhausted.")
        return {}
    
    return newFilteredList