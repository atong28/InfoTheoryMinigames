words = open('vocab.txt').readlines()

words = [word.strip() for word in words]

words = [word for word in words if all(letter in "abcdefghijklmnopqrstuvwxyz-'" for letter in word)]

with open('vocabStrict.txt', 'w') as f:
    f.write("\n".join(words))
    f.close()