f = open('wikipedia-english-list.txt', 'r')
content = f.read()

def splitText(entry):
    result = entry.split(" ")
    return (result[0], int(result[1]))

wordList = list(map(splitText, content.splitlines()))