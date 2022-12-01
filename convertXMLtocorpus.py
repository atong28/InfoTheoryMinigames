import xml.etree.ElementTree as ET
import os

directory = '/home/atong/bnc/Texts'

def iterateFiles(rootDirectory):
    sentences = []
    for filename in os.scandir(rootDirectory):
        if filename.is_dir():
            sentences += iterateFiles(filename.path)
        elif filename.path[-4:] == ".xml":
            sentences += parseSentences(filename.path)
    return sentences

def parseSentences(filename):
    print(f"Parsing {filename}")
    root = ET.parse(filename)

    sentences = []
    for wordElement in root.iter('s'):
        sentence = []
        for word in wordElement.iter('w'):
            if word.text:
                sentence.append(word.text.strip().lower())
        sentences.append(" ".join(sentence))

    return sentences

sentenceList = iterateFiles(directory)

with open('bnc-corpus.txt', 'w') as f:
    f.write("\n".join(sentenceList))
    f.close()