import numpy as np

f = open('top50k.txt', 'r', encoding='utf-8')
content = f.read()

def splitText(entry):
    result = entry.split(" ")
    return (result[0], int(result[1]))

wordList = list(map(splitText, content.splitlines()))

sortedList = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

for word in wordList:
    if len(word[0]) > 59: print(word)
    sortedList[len(word[0])].append(word)
    
print(sortedList[2])
    
