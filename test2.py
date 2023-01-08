viable = [['a', 'b', 'c'], ['d', 'e'], ['f', 'g', 'h', 'i']]

def generatePhrase(depth, current=''):
    for word in viable[depth]:
        if depth == 2:
            yield current + ' ' + word
        else:
            yield from generatePhrase(depth + 1, current + ' ' + word)
        
gen = generatePhrase(0)
while True:
    try: 
        print(next(gen))
    except StopIteration:
        break