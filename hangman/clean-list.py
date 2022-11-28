from lib.getWordlist import importList
import json

wordlist = importList()

with open('wikipedia-english-list-cleaned.json', 'w') as f:
    json.dump(wordlist, f, indent=4)