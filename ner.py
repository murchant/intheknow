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
    # get_entities("Reading are interested in signing Barnsley defender Andy Yiadom on a free transfer #ReadingFC #BarnsleyFC pic.twitter.com/K45MEvqJvI,,,#ReadingFC")
    #
    # nltk_method("Reading are interested in signing Barnsley defender Andy Yiadom on a free transfer #ReadingFC #BarnsleyFC pic.twitter.com/K45MEvqJvI,,,#ReadingFC")
    process_tweet()



def process_tweet():
    # CHECK DELIMETER
    df_transfer_true = pd.read_csv("info/possible_false.csv", sep=';', error_bad_lines=False, encoding="utf-8")
    for i, row in df_transfer_true.iterrows():
        tweet_text = row["text"]
        username = row["username"]
        print("--------------------")
        entities = get_entities(hashtag_remover(tweet_text))
        pplayers = get_potential_players(entities)
        pclubs = get_potential_clubs(entities)
        x = make_player_queries(pplayers)
        player_hit = query_confirmed_db(x)
        print("Iteration: " + str(i))
        if noise_filter(tweet_text)==True:
            if len(player_hit)>0:
                process_tweet_text(username, tweet_text, player_hit[0], pclubs)
            else:
                # TODO check for player  synonym
                coll_false = transferdb["labelled__false_tweets"]
                entry = {"username": username.strip(), "tweet_text": tweet_text.strip(), "label":"False"}
                coll_false.insert_one(entry)


def process_tweet_text(username,tweet, hit, pclubs):
    coll_true = transferdb["labelled_tweets"]
    coll_false = transferdb["labelled__false_tweets"]
    club_syns = transferdb["club_syns"]
    # TODO: check if tweet date is behind official move
    # TODO: handle negative tweets like ones containing "rejected"
    # TODO: check for player  synonym

    if club_check(hit['Moving to'], pclubs):
        for i in pclubs:
            entry = {"username": username.strip(), "tweet_text": tweet.strip(), "label":"True"}
            coll_true.insert_one(entry)
            return
    else:
        print(hit["Name"] + " possible rumour")
        print(tweet)
        print(hit)
        entry = {"username": username.strip(), "tweet_text": tweet.strip(), "label":"False"}
        coll_false.insert_one(entry)


def noise_filter(text):
    if ("rejected" in text) or ("turned down" in text) or ("XI" in text) or ("kit" in text) or ("renewed" in text) or ("renew" in text) or ("extension" in text) or ("more years" in text) or ("not interested" in text) or ("appointed manager" in text):
        return False
    else:
        return True

def club_check(cname, pclist):
    # club_syns = transferdb["club_syns"]
    syn_list = db.query_collection({"club":cname}, "club_syns", transferdb)
    if cname in pclist:
        return True
    else:
        for i in syn_list:
            if i in pclist:
                return True
    return False


def get_potential_players(ents):
    potentials=[]
    for (i,j) in ents:
        if j == "PERSON" or "ORG" or j== "GPE":
            potentials.append(i)
    return potentials

def get_potential_clubs(ents):
    potentials=[]
    for (i,j) in ents:
        if j == "ORG" or j== "GPE" or j=="NORP" or j=="PERSON":
            potentials.append(i)
    return potentials

def preprocess(sent):
    sent = nltk.word_tokenize(sent)
    sent = nltk.pos_tag(sent)
    return sent

def get_entities(text):
    ents=[]
    # u = unicode(text, 'utf-8')
    nlp = en_core_web_sm.load()
    doc = nlp(text)
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

def query_confirmed_db(qs):
    actual_player=[]
    for i in qs:
        x = db.query_collection(i, "confirmed_transfers", transferdb)
        if x.count() > 0:
            for i in x:
                # print("Hit!: "+ i["Name"])
                actual_player.append(i)
    # print(actual_player)
    return actual_player

def hashtag_remover(text):
    cleaned = text.replace("#", "")
    return cleaned


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
