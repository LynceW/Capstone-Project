'''
Copyright (C) 2018 Kaiming Kuang - All Rights Reserved

You may use, distribute and modify this code under the
terms of the GNU General Public License v3.0. There s-
hould be a copy of GPL 3.0 licence attached with this 
file.

Any questions please email kaiming.kuang@outlook.com

This is a program analyzing the sentiment of Bank of 
Canada statements. It used POS and IOB tags to analyze 
the grammar structure and then measure the sentiment u-
sing a keyword-modifier dictionary method.
'''

import pandas as pd
import funcs
import re                                           # Regular expression
import nltk                                         # Natural language toolkit
import numpy as np
import pickle                                       # Python pickle package. For temparaily saving data
from Chunker import Chunker                         # Chunker class for chunking sentences
from ShiftReduceParser import ShiftReduceParser     # ShiftReduceParser class for parsing texts
from Feature import Feature, Modifier               # Feature and Modifier class for saving feature and modifier data
from matplotlib import pyplot as plt
import sklearn
import matplotlib.dates
import warnings


# Turn off warning.
warnings.filterwarnings("ignore")

'''======== Part I: Load the statement data ========'''

# Load data.
data = pd.read_csv("BankOfCanada.csv")

# Convert the release dates into matplotlib format.
dates = [matplotlib.dates.datestr2num(date) for date in list(data["Date"].values)]

'''======== Part II: Data preprocessing ========'''
# In this part we first linked all the composite words that we manually found, tokenized (split the text into words) the
# text, and then linked the possessive words that are wrongly divided.

# Read the composite word file. Composite words are phrases that are really one entity. We need to use the
# ReplaceComposite function to convert them into words such as "GDP_growth".
compoWords = pd.read_csv("CompositeWordsFiltered.csv")["Word"]
data = funcs.ReplaceComposite(compoWords, data)

# Tokenizing the texts. We split the texts into words and then attach POS (Part-of-Speech) tags to them.
tokens = funcs.Tokenize(data)

# There are possessive words such as "Canada's" that are wrongly separated. We used the LinkPossessive function to link
# them.
tokens = funcs.LinkPossessive(tokens)

# Use pickle to save our tokens in binary format in txt file.
pickle.dump(tokens, open("tokens.txt", "wb"))
print("Tokenizing finished.")

'''======== Part III: Grammar induction ========'''
# In this part, we used the NLTK CoNLL2000 corpus, which contains 270 thousand words of Wall Street Journal, to induce
# grammar. The grammar is in the format of a CFG (Context-Free Grammar).

# Load the NLTK CoNLL2000 corpus.
grammarTrain = nltk.corpus.conll2000.chunked_sents()

# Convert the grammar trees in the corpus into a CFG (Context-Free Grammar).
grammar = funcs.InduceNonTerminal(grammarTrain)

# Save the grammar file.
pickle.dump(grammar, open("grammar.txt", "wb"))
print("Grammar induction finished.")

'''========= Part IV: Chunking ========'''
# In this part, we chunk sentences into different phrases using the IOB (Inside-Outside-Beginning) tags. There are 3 ki-
# nds of phrases: noun phrases (NP), verb phrases (VP) and preposition phrases (PP).

# Load the train and test dataset for chunking.
chunkTrain = nltk.corpus.conll2000.chunked_sents("train.txt")
chunkTest = nltk.corpus.conll2000.chunked_sents("test.txt")

# Initiate a Chunker object. Use the training corpus to train the chunker.
chunker = Chunker(chunkTrain)

# Evaluate the chunker's performance on the test corpus.
print(chunker.evaluate(chunkTest))

# Use the trained chunker to chunk our own texts.
chunkedSents = funcs.ChunkSents(tokens, chunker)

# Save the chunked texts.
pickle.dump(chunkedSents, open("chunked_sents.txt", "wb"))
print("Chunking finished.")

'''======== Part V: Deep parsing ========'''
# In this part, we used the grammar induced in previous step to parse our texts. Basically we used a shift-reduce parsi-
# ng algorithm to parse the texts and find out if there are larger phrases built on small phrases.

# Initiate a parser object. Load it with grammar.
parser = ShiftReduceParser(grammar)

# Use the parser to parse our own texts.
parsedSents = funcs.ParseTexts(chunkedSents, parser)

# Save the parsed texts.
pickle.dump(parsedSents, open("parsed_sents.txt", "wb"))
print("Parsing finished.")

'''======== Part VI: Sentiment Measuring ========'''
# Here we used the features (each feature contains many keywords) and modifiers to measure the sentiment of each text.
# The sentiment are categorized into hawkish (marked as 1), dovish (marked as -1) and neutral (marked as 0). The total
# sentiment is calculated as:
#       total sentiment = (# hawkish - # dovish) / (# hawkish + # dovish + # neutral)


# Load the modifiers.
modifiers = pickle.load(open("modifiers.txt", "rb"))

# Create all the features.
demandSupply = Feature("demand_supply", modifiers)
employment = Feature("employment", modifiers)
energy = Feature("energy", modifiers)
inflation = Feature("inflation", modifiers)
investCons = Feature("investment_consumption", modifiers)
macroeconomy = Feature("macroeconomy", modifiers)
policy = Feature("policy", modifiers)
risk = Feature("risk", modifiers)
features = [demandSupply, employment, energy, inflation, investCons, macroeconomy, policy, risk]

# Loop over all parsed texts to measure the sentiment of each statement.
sentiments = []

for record in parsedSents:

    sent, count = funcs.MeasureSentiment(record, features)
    sentiments.append(sent)

# Save the sentiment into a csv file.
sentiments = pd.DataFrame({"Date": dates, "Sentiment": sentiments})
sentiments.to_csv("sentiment.csv", index=False)
print("Finish analyzing. File saved.")