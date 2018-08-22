import nltk
import pandas as pd
import numpy as np
import re
import sys
from nltk.tokenize import sent_tokenize, word_tokenize
from matplotlib import pyplot as plt
import matplotlib.dates


def Tokenize(data):

    dataLen = data.shape[0]
    tokens = []

    for i in range(dataLen):

        sentList = sent_tokenize(data["Statement"][i])
        tokens.append([nltk.pos_tag(word_tokenize(sentence)) for sentence in sentList])

    newTokens = []

    for record in tokens:

        newRecord = []

        for sent in record:
            words = [tu[0].lower() for tu in sent]
            tags = [tu[1] for tu in sent]
            newSent = []

            for i in range(len(words)):

                if "_" in words[i]:
                    newSent.append((words[i], "NN"))
                else:
                    newSent.append((words[i], tags[i]))

            newRecord.append(newSent)

        newTokens.append(newRecord)

    tokens = newTokens

    return tokens


def GetCompositeWords(tokens):

    nounTags = ["NN", "NNS", "NNP", "NNPS"]         # the set of noun tags in Penn Treebank
    adjTags = ["JJ", "JJR", "JJS"]                  # the set of adj tags in Penn Treebank
    compoWords = []                                 # create an empty list to store composite nouns

    # loop over all sentences
    for record in tokens:

        for sentence in record:

            words = [x[0] for x in sentence]        # get all words in the current sentence
            posTags = [x[1] for x in sentence]      # get all POS tags
            sentLen = len(words)                    # the length of the current sentence

            '''
            the following part of code extracts composite words with two or more consecutive nouns
            '''

            i = 0                                   # initiate the index to 0
            flag = False                            # False: composite noun found. True: composite noun not found
            compoWord = ""                          # initiate empty string as composite noun

            # loop over all words in the current sentence
            while i < sentLen:

                if posTags[i] not in nounTags:              # if the current word isn't a noun

                    if flag and "_" in compoWord:           # if we have found at least two nouns in a row
                        compoWords.append(compoWord)        # add this composite noun to the list

                    compoWord = ""                          # clear the current compoWord
                    flag = False                            # reset the flag to False
                    i += 1                                  # continue to the next word
                    continue

                if not flag:                                # if the current word is a noun and flag is False
                    flag = True                             # this is the first of the composite. Turn on the flag
                    compoWord += words[i]                   # add the current word to the composite noun
                else:
                    compoWord += "_" + words[i]             # if the flag is on, add the noun preceded by an underline

                i += 1                                      # to the next word

            '''
            the following part of code extracts composite words that starts with 1 or more adj's followed by 1 or more nouns
            '''

            i = 0                                           # reset the index to 0
            nounFlag = False                                # False: nouns not found. True: nouns found
            adjFlag = False                                 # False: adj's not found. True: adj's found
            compoWord = ""                                  # create an empty string to store the composite word

            # loop over the whole sentence
            while i < sentLen:
                
                if posTags[i] in adjTags:                   # if the current word is an adj

                    if not nounFlag:                        # if we haven't found any noun previously
                        adjFlag = True                      # set the adjFlag to be True
                        if compoWord:                       # if the compoWord isn't empty
                            compoWord += "_" + words[i]     # add the current word preceded with an underline
                        else:
                            compoWord += words[i]           # else, just add the current word
                    else:                                   # if we did find nouns before
                        compoWords.append(compoWord)        # add the existing compoWord to the list
                        compoWord = ""                      # reset the compoWord variable to empty
                        adjFlag = False                     # reset the two flags to be False
                        nounFlag = False
                
                elif posTags[i] in nounTags:                # if the current word is a noun

                    if adjFlag:                             # if we have found adj's before
                        nounFlag = True                     # set the nounFlag to be true
                        compoWord += "_" + words[i]         # add the current word preceded with an underline
                
                i += 1

    compoWords = [word for word in compoWords if compoWords.count(word) > 1]
    tempWords = compoWords
    compoWords = list(set(compoWords))
    wordsCounts = [tempWords.count(word) for word in compoWords]

    return compoWords, wordsCounts


def LinkPossessive(tokens):

    nounTags = ["NN", "NNS", "NNP", "NNPS"]  # the set of noun tags in Penn Treebank

    for i in range(len(tokens)):

        for j in range(len(tokens[i])):

            newSent = []

            for k in range(0, len(tokens[i][j])):

                if k != 0:
                    (word, tag) = tokens[i][j][k]
                    (wordPrev, tagPrev) = tokens[i][j][k - 1]

                    if word == "'s" and tagPrev in nounTags:
                        newWord = wordPrev + word
                        newTag = "PRP$"
                        newSent.append((newWord, newTag))
                    else:
                        newSent.append((word, tag))

            tokens[i][j] = newSent

    return tokens


def TagsSince(sent, i):

    dtSet = set()
    vbSet = set()
    dtPattern = re.compile(r"DT")
    vbPattern = re.compile(r"VB.*")

    for _, pos in sent[:i]:

        if re.search(dtPattern, pos):
            dtSet = set()
        else:
            dtSet.add(pos)
        
        if re.search(vbPattern, pos):
            vbSet = set()
        else:
            vbSet.add(pos)
        
    return ("+".join(sorted(dtSet)), "+".join(sorted(vbSet)))


def GetFeatures(sent, i):

    word, pos = sent[i]
    sentLen = len(sent)

    if i != 0:
        _, prevTag = sent[i - 1]
    else:
        prevTag = "<START>"
    
    if i != sentLen - 1:
        _, nextTag = sent[i + 1]
    else:
        nextTag = "<END>"
    
    tagsSince = TagsSince(sent, i)
    lookBack = "{}+{}".format(prevTag, pos)
    lookAhead = "{}+{}".format(pos, nextTag)

    features = {
        "word": word,
        "pos": pos,
        "prevPos": prevTag,
        "nextPos": nextTag,
        "prevCurr": lookBack,
        "currNext": lookAhead,
        "tagsSinceDt": tagsSince[0],
        "tagsSinceVb": tagsSince[1]
    }

    return features


def ReplaceComposite(compoWords, data):

    for i in range(data.shape[0]):
        text = data["Statement"][i]
        newText = text

        for phrase in compoWords:
            tempPhrase = re.sub(r"_", " ", phrase)
            newText = re.sub(tempPhrase, phrase, newText)

        data["Statement"][i] = newText

    return data


def CountWords(tokens):

    count = {}

    for record in tokens:

        for sent in record:

            for w, _ in sent:

                count[w] = count.get(w, 0) + 1

    regPattern = re.compile(r"NN.*|VB.*|JJ.*|RB.*")

    words = []
    counts = []

    for word in count.keys():

        pos = nltk.pos_tag([word])[0][1]

        if re.search(regPattern, pos):
            words.append(word)
            counts.append(count[word])

    count = pd.DataFrame(counts, index=words)
    count.to_csv("word_counts.csv", index=True)

    return


def ChunkSents(tokens, chunker):

    chunkedSents = [[chunker.parse(sent) for sent in record] for record in tokens]

    return chunkedSents


def InduceSentGrammar(sent):

    nonTerminal = []
    treeType = type(sent)
    parentOverall = sent.label()
    childrenOverall = [tree.label() if isinstance(tree, treeType) else tree[1] for tree in sent]
    nonTerminal.append((parentOverall, childrenOverall))

    for tree in sent:

        if isinstance(tree, treeType):
            nonTerminal += InduceSentGrammar(tree)

    return nonTerminal


def ConvertPosTag(tag):

    if re.search(r"NN.*|VB.*|JJ.*|RB.*", tag):
        tag = tag[:2]

    return tag


def InduceNonTerminal(sents):

    nonTerminalGrammar = []
    for sent in sents:
        nonTerminalGrammar += InduceSentGrammar(sent)

    temp = []
    for grammar in nonTerminalGrammar:

        if grammar not in temp:

            lhs = grammar[0]
            rhs = [ConvertPosTag(pos) for pos in grammar[1]]
            newGrammar = (lhs, rhs)
            temp.append(newGrammar)

    nonTerminalGrammar = [production for production in temp if production[0] != "S"]

    return nonTerminalGrammar


def Lemmatize(words):

    if isinstance(words, str):
        words = [words]
    pos = nltk.pos_tag(words)
    
    modeDict = {
        "NN": "n",
        "VB": "v",
        "JJ": "a",
        "RB": "r"
        }
    
    lemma = []
    lemmatizer = nltk.stem.WordNetLemmatizer()
    pattern = re.compile(r"^NN.*|^VB.*|^JJ.*|^RB.*")
    
    for i in range(len(words)):
        
        if re.search(pattern, pos[i][1]):
            mode = modeDict[pos[i][1][0] + pos[i][1][1]]
            lemma.append(lemmatizer.lemmatize(words[i], pos=mode))
        else:
            lemma.append(words[i])

    if len(lemma) == 1:
        lemma = lemma[0]

    return lemma


def ParseTexts(tokens, parser):

    trees = [[parser.parse(sent) for sent in record] for record in tokens]

    return trees


def Traverse(sent):

    phrases = [tree.leaves() for tree in sent\
               if not isinstance(tree, tuple) and len(tree.leaves()) >= 2]

    return phrases


def MeasureSentiment(record, features):

    hawkish = 0
    dovish = 0
    neutral = 0

    for feature in features:

        sentiment = feature.measure(record)
        hawkish += sentiment[0]
        dovish += sentiment[1]
        neutral += sentiment[2]
    try:
        totalSentiment = (hawkish - dovish) / (hawkish + dovish + neutral)
    except:
        totalSentiment = 0

    return totalSentiment, hawkish + dovish + neutral
