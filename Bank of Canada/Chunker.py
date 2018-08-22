import nltk
import funcs


class Tagger(nltk.TaggerI):

    def __init__(self, train):

        trainSet = []

        for sent in train:

            untaggedSent = nltk.tag.untag(sent)

            for i, (_, tag) in enumerate(sent):

                features = funcs.GetFeatures(untaggedSent, i)
                trainSet.append((features, tag))
        
        self.classifier = nltk.MaxentClassifier.train(trainSet, trace=0)
    
    def tag(self, sent):
        
        iobs = []

        for i, _ in enumerate(sent):

            features = funcs.GetFeatures(sent, i)
            tag = self.classifier.classify(features)
            iobs.append(tag)

        return zip(sent, iobs)


class Chunker(nltk.ChunkParserI):

    def __init__(self, train):

        taggedSent = [[((w, t), c) for (w, t, c) in nltk.chunk.tree2conlltags(sent)] for sent in train]
        self.tagger = Tagger(taggedSent)
    
    def parse(self, sent):

        taggedSent = self.tagger.tag(sent)
        tree = nltk.chunk.conlltags2tree([(w, t, c) for ((w, t), c) in taggedSent])

        return tree
