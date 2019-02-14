import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import conlltags2tree, tree2conlltags, ne_chunk
from pprint import pprint
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
import pymongo
from pymongo import MongoClient
import db
import pandas as pd

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
transferdb = myclient["transferdb"]

def main():
    print("hi")
    process_tweet()


def process_tweet():
    coll = transferdb["labelled_tweets"]
    df_transfer_true = pd.read_csv("info/true_data_set.csv", sep=';', error_bad_lines=False, encoding="utf-8")
    for i, row in df_transfer_true.iterrows():
        tweet_text = row["text"]
        username = row["username"]
        entities = get_entities(tweet_text)
        pplayers = get_potential_players(entities)
        pclubs = get_potential_clubs(entities)
        x = make_player_queries(pplayers)
        player_hit = query_db(x)
        if len(player_hit)>0:
            process_tweet_text(username,tweet_text, player_hit[0], pclubs)

def process_tweet_text(tweet, hit, pclubs):
    coll = transferdb["labelled_tweets"]
    for i in pclubs:
        if hit['Moving to'] == i:
            print(hit["Name"] + " to " + i)
            entry = {"username": username.strip(), "tweet_text": tweet.strip(), "label":"True"}
            coll.insert_one(entry)

def verify_label(cursor):
    print(cursor["Moving to"])


def get_potential_players(ents):
    potentials=[]
    for (i,j) in ents:
        if j == "PERSON":
            potentials.append(i)
    return potentials

def get_potential_clubs(ents):
    potentials=[]
    for (i,j) in ents:
        if j == "ORG" or j== "GPE" or j=="NORP":
            potentials.append(i)
    return potentials

def preprocess(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)
    return sent

def get_entities(text):
    ents=[]
    u = unicode(text, 'utf-8')
    nlp = en_core_web_sm.load()
    doc = nlp(u)
    # pprint([(X.text, X.label_) for X in doc.ents])
    for i in doc.ents:
        ents.append((i.text, i.label_))
    return ents

def make_player_queries(names):
    querys=[]
    for i in names:
        q = {"Name": i}
        querys.append(q)
    return querys

def query_db(qs):
    actual_player=[]
    for i in qs:
        x = db.query_collection(i, "confirmed_transfers", transferdb)
        if x.count() > 0:
            for i in x:
                print("Hit!: "+ i["Name"])
                actual_player.append(i)
    return actual_player


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

if __name__ == '__main__':
    main()
