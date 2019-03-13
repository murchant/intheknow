# -*- coding: utf-8 -*-
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
import math
import pandas as pd
from six import string_types
import plac
import random
from pathlib import Path
from spacy.util import minibatch, compounding

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
transferdb = myclient["transferdb"]



def main():
    # get_entities(unicode("Confirmed: Blackburn complete deal for Ben Brereton"))
    #
    # nltk_method("Reading are interested in signing Barnsley defender Andy Yiadom on a free transfer #ReadingFC #BarnsleyFC pic.twitter.com/K45MEvqJvI,,,#ReadingFC")
    # filter_pfalse()
    # ex= ["Fenerbahce move would be a 'backwards step' for Jack Wilshere, says former Arsenal midfielder Adrian Clarke: Jack Wilshere has been urged not to join Fenerbahce this summer, as he would be taking a 'backwards step' in his career. Latest reports c", "Liverpool are keen on signing Arsenal midfielder Aaron Ramsey", "Arsenal boss Unai Emery is plotting a 25m move for Croatian defender", "Arsenal striker Lucas Perez has undergone a medical at West Ham", "Fulham sign Arsenal defender Calum Chambers on season-long loan", "Barcelona Transfer News: Ousmane Dembele Rules out Exit Amid Arsenal Rumours"]

    # retrain_nlp_model(unicode("Arsenal",encoding="utf-8"), ex)
    # retrain_batch(retrain_data2)
    process_tweet()
    # res = english_club_check([u'Leeds', u'Caleb Ekuban', u'Trabzonspor'])
    # print(res)
    return


def filter_pfalse():
    coll_true = transferdb["pfalse_ttalk"]
    df_pfalse = pd.read_csv("info/possible_false.csv", sep=';', error_bad_lines=False, encoding="utf-8")
    print(len(df_pfalse.index))
    for i, row in df_pfalse.iterrows():
        tweet_text = row["text"]
        username = row["username"]
        if(i>len(df_pfalse.index)):
            break
        if transfer_talk_check(tweet_text)==True:
            df_pfalse = df_pfalse.drop(df_pfalse.index[i])  # this aint working
    df_pfalse.to_csv("info/filtered_pfalse.csv", encoding='utf-8', sep=';')
    print(len(df_pfalse.index))

def transfer_talk_check(text):

    if(isinstance(text, basestring)):

        if all(x in text for x in ["transfer", "confirmed"]) or ("medical" in text) or all(x in text for x in ["signing", "confirmed"]) or all(x in text for x in ["verge", "signing"]) or all(x in text for x in ["transfer", "complete"]) or ("in talks" in text) or ("in contract talks" in text) or all(x in text for x in ["transfer", "arrived"]) or all(x in text for x in ["loan", "signed"]):
            return True
        else:
            return False

def english_club_check(clubs):
    # for i in clubs:
    #     query = {"Name:" i}
    #     res = query_collection(query, "english_clubs", transferdb)
    #     if len(res)>0:
    #         return True

    queryname = {"Name": {"$in": clubs}}
    res = db.query_collection(queryname, "english_clubs", transferdb)
    querysyn = {"syns": {"$in": clubs}}
    ressyn = db.query_collection(querysyn, "english_clubs", transferdb)
    if res.count() > 0:
        return True # res[0]["Name"]
    elif ressyn.count() > 0:
        return True # ressyn[0]["Name"]
    else:
        return False

def process_tweet():
    # CHECK DELIMETER
    df_transfer_true = pd.read_csv("info/query_terms.csv", sep=';', error_bad_lines=False, encoding="utf-8")
    df_transfer_true = df_transfer_true.drop(df_transfer_true.index[0:11199])
    for i, row in df_transfer_true.iterrows():
        tweet_text = row["text"]
        username = row["username"]
        print("--------------------")
        # print(tweet_text)
        entities = get_entities(hashtag_remover(tweet_text))
        pplayers = get_potential_players(entities)
        pclubs = get_potential_clubs(entities)
        x = make_player_queries(pplayers)
        player_hit = query_confirmed_db(x)
        print("Iteration: " + str(i))
        print(pclubs)
        if english_club_check(pclubs):
            print("English club")
            if noise_filter(tweet_text)==True:
                if transfer_talk_check(tweet_text):
                    if len(player_hit)>0:
                        process_tweet_text(username, tweet_text, player_hit[0], pclubs)
                    else:
                        # TODO check for player synonym
                        if len(pplayers)>0:
                            coll_false = transferdb["labelled__false_querys"]
                            entry = {"username": username.strip(), "tweet_text": tweet_text.strip(), "label":"False"}
                            coll_false.insert_one(entry)



def process_tweet_text(username,tweet, hit, pclubs):
    coll_true = transferdb["labelled_tweets"]
    coll_false = transferdb["labelled__false_querys"]
    club_syns = transferdb["club_syns"]
    # TODO: check if tweet date is behind official move
    # TODO: handle negative tweets like ones containing "rejected"
    # TODO: check for player  synonym

    if club_check(hit['Moving to'], pclubs):
        for i in pclubs:
            entry = {"username": username.strip(), "tweet_text": tweet.strip(), "label":"True"}
            # coll_true.insert_one(entry)
            return
    else:
        print(hit["Name"] + " possible rumour")
        print(tweet)
        print(hit)
        entry = {"username": username.strip(), "tweet_text": tweet.strip(), "label":"False"}
        coll_false.insert_one(entry)


def noise_filter(text):
    if ("rejected" in text) or ("injury" in text) or ("turned down" in text) or ("XI" in text) or ("kit" in text) or ("renewed" in text) or ("renew" in text) or ("extension" in text) or ("more years" in text) or ("not interested" in text) or ("appointed manager" in text) or ("Highlights" in text) or ("All Goals" in text) or ("Friendly" in text) or ("FT" in text)  or ("appearance" in text) or ("bet" in text) or ("odds" in text) or ("refused" in text) or ("vs" in text) or ("recovery" in text) or ("denied" in text) or ("fans react" in text) or ("new contract" in text) or ("called off" in text) or ("abandoned" in text) or ("broke down" in text) or all(x in text for x in ["not", "allowed"]):
        return False
    else:
        return True


# Rethink how you're checking here, nicknames could be scraped
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
    nlp = spacy.load("./retrained_model")
    doc = nlp(text)
    pprint([(X.text, X.label_) for X in doc.ents])
    for i in doc.ents:
        ents.append((i.text, i.label_))
    return ents


def retrain_batch(batch):
    for ent, exs in batch.iteritems():
        print("Training: " + ent)
        retrain_nlp_model(ent, exs)


def retrain_nlp_model(entity, examples):
    TRAIN_DATA = []
    n_iter = 100
    output_dir = "./retrained_model"
    for i in examples:
        if entity in i:
            start = i.index(entity)
            end = start+len(entity)
            entry = (unicode(i.decode('utf-8')), {'entities': [(start, end, 'ORG')]})
            TRAIN_DATA.append(entry)

     # """Load the model, set up the pipeline and train the entity recognizer."""
    nlp = en_core_web_sm.load()  # load existing spaCy model
    # print("Loaded model '%s'")

    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner, last=True)
    # otherwise, get it so we can add labels
    else:
        ner = nlp.get_pipe("ner")

    # add labels
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):  # only train NER
        # reset and initialize the weights randomly but only if we're
        # training a new model
        nlp.begin_training()
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(
                    texts,  # batch of texts
                    annotations,  # batch of annotations
                    drop=0.5,  # dropout - make it harder to memorise data
                    losses=losses,
                )
            print("Losses", losses)

    # test the trained model
    for text, _ in TRAIN_DATA:
        doc = nlp(text)
        print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
        print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        # print("Loading from", output_dir)
        # nlp2 = spacy.load(output_dir)
        # for text, _ in TRAIN_DATA:
        #     doc = nlp2(text)
        #     print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
        #     print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])

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
    if(isinstance(text, string_types)):
        cleaned = text.replace("#", "")
        return cleaned
    else:
        return text

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
