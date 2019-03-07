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
    df_transfer_true = pd.read_csv("info/possible_false.csv", sep=';', error_bad_lines=False, encoding="utf-8")
    # df_transfer_true = df_transfer_true.drop(df_transfer_true.index[0:3434])
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


wrongly_labelled = ["5c802abbe8e5df1f0d6e8791", "5c802abce8e5df1f0d6e8792", "5c802b18e8e5df1f0d6e8794", "5c802b25e8e5df1f0d6e8795", "5c802b2be8e5df1f0d6e8796", "5c802b3ce8e5df1f0d6e8797", "5c802b7ae8e5df1f0d6e8799", "5c802b82e8e5df1f0d6e879b", "5c802ba0e8e5df1f0d6e879d", "5c802ba6e8e5df1f0d6e879e", "5c802ba9e8e5df1f0d6e87a0", "5c802c7be8e5df1f0d6e87a2", "5c802c90e8e5df1f0d6e87a4", "5c802c90e8e5df1f0d6e87a4", "5c802cace8e5df1f0d6e87a8", "5c802caee8e5df1f0d6e87a9", "5c802ccfe8e5df1f0d6e87aa", "5c802d4be8e5df1f0d6e87ab", "5c802d77e8e5df1f0d6e87ad", "5c802dcce8e5df1f0d6e87ae", "5c802de2e8e5df1f0d6e87b0", "5c802e9ce8e5df1f0d6e87b5", "5c802f58e8e5df1f0d6e87ba", "5c802f58e8e5df1f0d6e87ba", "5c802fb3e8e5df1f0d6e87be", "5c802fcfe8e5df1f0d6e87bf", "5c802fcfe8e5df1f0d6e87bf", "5c803006e8e5df1f0d6e87c4", "5c8030bbe8e5df1f0d6e87ca", "5c8030f3e8e5df1f0d6e87cb", "5c8031bde8e5df1f0d6e87d1", "5c80321ae8e5df1f0d6e87d3", "5c80321ce8e5df1f0d6e87d4", "5c803220e8e5df1f0d6e87d5", "5c803223e8e5df1f0d6e87d7", "5c803223e8e5df1f0d6e87d7", "5c803225e8e5df1f0d6e87d8", "5c803234e8e5df1f0d6e87db", "5c803238e8e5df1f0d6e87dd", "5c803241e8e5df1f0d6e87df", "5c803242e8e5df1f0d6e87e0", "5c803243e8e5df1f0d6e87e1", "5c80324ee8e5df1f0d6e87e2", "5c8032a8e8e5df1f0d6e87e6", "5c8032a9e8e5df1f0d6e87e7", "5c8032cbe8e5df1f0d6e87e9", "5c8032d5e8e5df1f0d6e87eb", "5c8032d8e8e5df1f0d6e87ec", "5c8032d8e8e5df1f0d6e87ed", "5c8032fae8e5df1f0d6e87ef", "5c803302e8e5df1f0d6e87f0", "5c8033dae8e5df1f0d6e87f4", "5c8033f0e8e5df1f0d6e87f5", "5c8033f8e8e5df1f0d6e87f6", "5c8033f9e8e5df1f0d6e87f7", "5c80343de8e5df1f0d6e87f9", "5c8034f9e8e5df1f0d6e87fd", "5c803519e8e5df1f0d6e8800", "5c803567e8e5df1f0d6e8803", "5c80358be8e5df1f0d6e8805", "5c803593e8e5df1f0d6e8806", "5c803597e8e5df1f0d6e8807", "5c8035ace8e5df1f0d6e8809", "5c803627e8e5df1f0d6e880c", "5c80362ae8e5df1f0d6e880d", "5c80362be8e5df1f0d6e880e", "5c803657e8e5df1f0d6e8812", "5c80366fe8e5df1f0d6e8813", "5c803672e8e5df1f0d6e8814", "5c803686e8e5df1f0d6e8816", "5c803695e8e5df1f0d6e8818", "5c8036d5e8e5df1f0d6e8819", "5c8036d6e8e5df1f0d6e881a", "5c8036eee8e5df1f0d6e881c", "5c8036f5e8e5df1f0d6e881d", "5c803772e8e5df1f0d6e8822", "5c80379ae8e5df1f0d6e8824", "5c80379be8e5df1f0d6e8825", "5c8037eae8e5df1f0d6e8829", "5c80382ee8e5df1f0d6e882a", "5c803892e8e5df1f0d6e882c", "5c8038b0e8e5df1f0d6e882d", "5c8038b6e8e5df1f0d6e882e", "5c8038bce8e5df1f0d6e882f", "5c8038bfe8e5df1f0d6e8830", "5c8038cae8e5df1f0d6e8831", "5c8038e9e8e5df1f0d6e8832", "5c80393ce8e5df1f0d6e8833", "5c803974e8e5df1f0d6e8834", "5c803981e8e5df1f0d6e8835", "5c803a55e8e5df1f0d6e883c", "5c803a74e8e5df1f0d6e883d", "5c803ac1e8e5df1f0d6e8840", "5c803ad0e8e5df1f0d6e8841", "5c803b45e8e5df1f0d6e8846", "5c803b52e8e5df1f0d6e8847", "5c803b61e8e5df1f0d6e8849", "5c803b7fe8e5df1f0d6e884a", "5c803ba7e8e5df1f0d6e884b", "5c803babe8e5df1f0d6e884c", "5c803bbfe8e5df1f0d6e884d", "5c803c59e8e5df1f0d6e884e", "5c803ce2e8e5df1f0d6e8851", "5c803cfae8e5df1f0d6e8854", "5c803d1ce8e5df1f0d6e8856", "5c803d1ee8e5df1f0d6e8857", "5c803d27e8e5df1f0d6e8858", "5c803d30e8e5df1f0d6e8859", "5c803d52e8e5df1f0d6e885c", "5c803df6e8e5df1f0d6e885d", "5c803dfae8e5df1f0d6e885f", "5c803e14e8e5df1f0d6e8861", "5c803e15e8e5df1f0d6e8862", "5c803e29e8e5df1f0d6e8864", "5c803e2be8e5df1f0d6e8865", "5c803e42e8e5df1f0d6e8868", "5c803e92e8e5df1f0d6e886a", "5c803ec1e8e5df1f0d6e886c", "5c803ec3e8e5df1f0d6e886e", "5c803ed8e8e5df1f0d6e886f", "5c803ee6e8e5df1f0d6e8872", "5c803ee8e8e5df1f0d6e8873", "5c803faae8e5df1f0d6e8875", "5c80401ce8e5df1f0d6e8877", "5c80403ce8e5df1f0d6e8879", "5c804066e8e5df1f0d6e887b", "5c80406fe8e5df1f0d6e887c", "5c80409ce8e5df1f0d6e887d", "5c80409de8e5df1f0d6e887e", "5c8040cce8e5df1f0d6e8880", "5c804150e8e5df1f0d6e8883", "5c804195e8e5df1f0d6e8885", "5c8041b6e8e5df1f0d6e8887", "5c8041bee8e5df1f0d6e8888", "5c80421be8e5df1f0d6e8889", "5c804228e8e5df1f0d6e888a", "5c804265e8e5df1f0d6e888c", "5c8042c1e8e5df1f0d6e888f", "5c8042e3e8e5df1f0d6e8892", "5c8042ffe8e5df1f0d6e8895", "5c804310e8e5df1f0d6e8898", "5c804314e8e5df1f0d6e8899", "5c804316e8e5df1f0d6e889a", "5c80431ae8e5df1f0d6e889b", "5c80433ae8e5df1f0d6e889d", "5c804397e8e5df1f0d6e88a0", "5c8043c7e8e5df1f0d6e88a2", "5c8043fee8e5df1f0d6e88a6", "5c804403e8e5df1f0d6e88a7", "5c80442de8e5df1f0d6e88a8", "5c804467e8e5df1f0d6e88a9", "5c8044a3e8e5df1f0d6e88ad", "5c804587e8e5df1f0d6e88af", "5c8045ace8e5df1f0d6e88b0", "5c8045c4e8e5df1f0d6e88b1", "5c804608e8e5df1f0d6e88b3", "5c80460ce8e5df1f0d6e88b5", "5c804639e8e5df1f0d6e88b7", "5c80466ce8e5df1f0d6e88bc", "5c804696e8e5df1f0d6e88bd", "5c8046a0e8e5df1f0d6e88be", "5c8046a4e8e5df1f0d6e88bf", "5c804794e8e5df1f0d6e88c5", "5c8048afe8e5df1f0d6e88c8", "5c8048f1e8e5df1f0d6e88ca", "5c8049cee8e5df1f0d6e88cd", "5c8049ede8e5df1f0d6e88ce", "5c804a02e8e5df1f0d6e88cf", "5c804a46e8e5df1f0d6e88d0", "5c804a48e8e5df1f0d6e88d1", "5c804a4ae8e5df1f0d6e88d2", "5c804a5fe8e5df1f0d6e88d3", "5c804b0ce8e5df1f0d6e88d9", "5c804b58e8e5df1f0d6e88db", "5c804be1e8e5df1f0d6e88e0", "5c804cbde8e5df1f0d6e88e7", "5c804d0fe8e5df1f0d6e88eb", "5c804d57e8e5df1f0d6e88ed", "5c804da9e8e5df1f0d6e88f0", "5c804daee8e5df1f0d6e88f1", "5c804dd8e8e5df1f0d6e88f3", "5c804e1fe8e5df1f0d6e88f4", "5c804e2de8e5df1f0d6e88f6", "5c804ea1e8e5df1f0d6e88fc", "5c804eafe8e5df1f0d6e88fe", "5c804ebfe8e5df1f0d6e88ff", "5c804ec9e8e5df1f0d6e8901", "5c804eeae8e5df1f0d6e8902", "5c804f06e8e5df1f0d6e8904", "5c80510de8e5df1f0d6e890b", "5c805117e8e5df1f0d6e890c", "5c805185e8e5df1f0d6e890e", "5c8051c7e8e5df1f0d6e890f", "5c8051cde8e5df1f0d6e8910", "5c8051f5e8e5df1f0d6e8912", "5c8052b9e8e5df1f0d6e8916", "5c80537fe8e5df1f0d6e891e", "5c8053ade8e5df1f0d6e8920", "5c8053d7e8e5df1f0d6e8921", "5c8054b5e8e5df1f0d6e8924", "5c8054f5e8e5df1f0d6e8926", "5c8055c6e8e5df1f0d6e892d", "5c8055d8e8e5df1f0d6e892e", "5c8055e3e8e5df1f0d6e892f", "5c805607e8e5df1f0d6e8931", "5c8057a7e8e5df1f0d6e8934", "5c8057b8e8e5df1f0d6e8935", "5c8057c9e8e5df1f0d6e8937", "5c805890e8e5df1f0d6e893d", "5c8058ece8e5df1f0d6e893f", "5c80abace8e5df1f0d6e8941", "5c80cbfae8e5df1f0d6e8942", "5c80da87e8e5df1f0d6e8947", "5c80daa1e8e5df1f0d6e8948", "5c80daa3e8e5df1f0d6e8949", "5c80daabe8e5df1f0d6e894a", ""]

if __name__ == '__main__':
    main()
