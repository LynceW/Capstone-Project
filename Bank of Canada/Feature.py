import nltk
import funcs
import pandas as pd


class Feature():

    def __init__(self, feature, modifiers):

        self.feature = feature
        fileName = "features/{}.csv".format(self.feature)
        self.sentiment = pd.read_csv(fileName, index_col=0)
        self.keywords = list(self.sentiment.index)
        self.modifiers = modifiers
        self.modifiersList = list(self.sentiment.columns)
        self.sentiment = self.sentiment.values
    
    def measure(self, record):

        sentimentDict = {1: 0,
                         0: 0,
                         -1: 0}

        for sent in record:

            phrases = funcs.Traverse(sent)

            for phrase in phrases:

                phrase = [funcs.Lemmatize(x[0]) for x in phrase]

                for keyword in self.keywords:

                    if keyword in phrase:

                        for modifier in self.modifiers:

                            main = modifier.main
                            leaves = modifier.leaves

                            for word in leaves:

                                if funcs.Lemmatize(word) in phrase:

                                    row = self.keywords.index(keyword)
                                    col = self.modifiersList.index(main)
                                    sentiment = self.sentiment[row, col]
                                    sentimentDict[sentiment] += 1
        
        hawkish, dovish, neutral = sentimentDict[1], sentimentDict[-1], sentimentDict[0]
        
        return (hawkish, dovish, neutral)


class Modifier():

    def __init__(self, main, leaves):

        self.main = main
        self.leaves = leaves

    def __str__(self):

        leavesStr = "[{}]".format(", ".join(self.leaves))
        string = "({}, {})".format(self.main, leavesStr)

        return string

    def draw(self):

        nltk.tree.Tree(self.main, self.leaves).draw()

        return