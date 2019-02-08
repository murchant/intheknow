import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import conlltags2tree, tree2conlltags, ne_chunk
from pprint import pprint
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm

def main():
    # SPACEY #####
    ex = "Leicester keen on Portos Pereira: Leicester City are interested in signing Porto right back Ricardo Pereira , Sky Sports News has learned, as Claude Puel considers options to strengthen his defence this summer"
    u = unicode(ex, 'utf-8')
    nlp = en_core_web_sm.load()
    doc = nlp(u)
    pprint([(X.text, X.label_) for X in doc.ents])

    # SPACEY #####

def nltk_method(str):
    # INSTALL
    # nltk.download()
    # nltk.download('averaged_perceptron_tagger')
    # nltk.download('maxent_ne_chunker')
    # nltk.download('words')

    ex = str
    u = unicode(ex, 'utf-8')
    pattern = 'NP: {<DT>?<JJ>*<NN>}'
    sent = preprocess(ex)
    cp = nltk.RegexpParser(pattern)
    cs = cp.parse(sent)
    iob_tagged = tree2conlltags(cs)
    ne_tree = ne_chunk(pos_tag(word_tokenize(ex)))
    print(ne_tree)

def preprocess(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)
    return sent

if __name__ == '__main__':
    main()
