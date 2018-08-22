import nltk
import funcs


class ShiftReduceParser():

    def __init__(self, grammar):

        self.grammar = grammar
    
    def parse(self, sent):

        lhs = [pair[0] for pair in self.grammar]
        rhs = [pair[1] for pair in self.grammar]

        stack = []
        index = 0
        shift = True

        while index != len(sent):

            reduce = False
            
            if shift:
                stack.append(sent[index])
                index += 1
            
            tags = [x.label() if not isinstance(x, tuple)\
                    else funcs.ConvertPosTag(x[1]) for x in stack]
            
            for i in range(len(stack)-2, -1, -1):

                if tags[i:] in rhs:

                    shift = False
                    reduce = True
                    parent = lhs[rhs.index(tags[i:])]
                    children = stack[i:]
                    tree = nltk.tree.Tree(parent, children)
                    stack = stack[:i]
                    stack.append(tree)
                    break
            
            if not reduce: shift = True
            

        s = nltk.Nonterminal("S")
        tree = nltk.tree.Tree(s, stack)

        return tree
        