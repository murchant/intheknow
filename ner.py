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
    # get_entities(unicode("Chelsea transfer news: Blues flop Tiemoue Bakayoko close to AC Milan loan move: Chelsea are in talks with AC Milan over a potential loan deal for Tiemoue Bakayok"))
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
        if ("transfer" in text) or ("medical" in text) or ("signing" in text) or ("verge" in text) or ("complete" in text) or ("accepted" in text) or ("transfer news" in text) or ("in talks" in text) or ("arrived" in text) or ("move" in text) or ("loan" in text) or ("agree" in text) or ("target" in text) or ("transfer window" in text) or ("re-signed" in text):
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
        if english_club_check(pclubs)==True:
            print("English club")
            if noise_filter(tweet_text)==True:
                if transfer_talk_check(tweet_text)==True:
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
    if ("rejected" in text) or ("injury" in text) or ("turned down" in text) or ("XI" in text) or ("kit" in text) or ("renewed" in text) or ("renew" in text) or ("extension" in text) or ("more years" in text) or ("not interested" in text) or ("appointed manager" in text) or ("Highlights" in text) or ("All Goals" in text) or ("Friendly" in text) or ("FT" in text)  or ("appearance" in text) or ("bet" in text) or ("odds" in text) or ("refused" in text) or ("vs" in text) or ("recovery" in text) or ("denied" in text) or ("fans react" in text):
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
    # pprint([(X.text, X.label_) for X in doc.ents])
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

retrain_data2 = {"Cheslea":["Liverpool transfer news: Nabil Fekir twist as Lyon wait for Man Utd and Chelsea bids #epl", "Milan target loan deal for Chelsea midfielder Tiemoue Bakayoko #epl : Chelsea player Tiemoue Bakayoko has been linked with a loan move to AC Milan", "Chelsea star speaks out on Thibaut Courtois transfer #epl : Chelsea striker Olivier Giroud has spoken out about the potential transfer of Thibaut Courtois to Real Madrid as the deal looks to be edging closer.", "Chelsea manager Maurizio Sarri says there are no concerns about Eden Hazard leaving", "Club-record Kepa deal is a BIG risk for Chelsea', warns former Blues goalkeeper Mark Schwarzer: Former Chelsea goalkeeper Mark Schwarzer has warned the Blue", "Chelsea transfer news: Blues flop Tiemoue Bakayoko close to AC Milan loan move: Chelsea are in talks with AC Milan over a potential loan deal for Tiemoue Bakayok", "Chelsea's record-breaking goalkeeper move: Here are all the latest transfer rumours and news from Wednesday", "Chelsea transfer news: Blues in talks to sign Real Madrid star Mateo Kovacic on loan: Chelsea could sign Real Madrid star Mateo Kovacic on loan in the coming hours, according to reports.", "Kepa is a talent we have admired for a long time and we are extremely excited about his arrival. He has already demonstrated fantastic quality and consistency and will be a big part of any success Chelsea have in the coming years", "an accumulation of things, and I am very glad Chelsea has decided to trust me and to take me in as well.", "helsea target flying into London today to finalise move #epl : Kepa is due to fly into London today as he closes in on a move to Chelsea from Athletic Bilbao. Spanish outlet AS report that the deal is close with Chelsea"], "AC Milan": ["AC Milan left-back Ricardo Rodriguez after it has been", "AC Milan enter advanced talks over move for 40m Chelsea flop", "Everton move to beat AC Milan to Bakayoko signing", " Blues flop Tiemoue Bakayoko close to AC Milan loan move: Chelsea are in talks with AC Milan over a potential loan deal for Tiemoue Bakayoko, according to reports", "Bakayoko's agents, including his brother, are meeting right now in Milan the General manager AC Milan Leonardo", "Kovacic's arrival will trigger the departure of Tiemoue Bakayoko, who is set to join AC Milan on a season-long loan"], "Everton": ["Bernard is currently travelling from Brazil and is expected to arrive on Merseyside this afternoon ahead of a medical at Everton", "Everton are hoping Kurt Zouma will help solve their search for defensive reinforcements. The Toffees are increasingly confident of landing the 23-year-old French stopper on loan from Chelsea for the season", "Arsenal are willing to listen to offers for Danny Welbeck, with Premier League trio Everton, Bournemouth and Southampton interested, the London Evening Standard reports.", "Crystal Palace are considering re-signing Yannick Bolasie from Everton", "Everton have fought off competition from Chelsea, Atletico Madrid and West Ham to secure the signing of Brazilian winger Bernard", "Tottenham missing out on Bernard to Everton will be a kick in the teeth for Poch", "Leicester City have completed the signing of AS Monaco winger Rachid Ghezzal for an undisclosed fee", "andreva could be included in a deal with Monaco involving a loan swap, but all the parties involved have yet to give the green light for the completion.", "Thomas Lemar has described himself as very happy to be at Atletico Madrid after the La Liga side confirmed his transfer from Monaco", "Chelsea target Aleksandr Golovin has agreed to join Monaco", "DEAL DONE Wolves have signed Joao Moutinho from Monaco on a two-year deal"], "Derby County": ["Brentford have accepted an offer from Derby County for Florian Jozefzoon", "Derby boss Lampard believes Mount genuine England class #epl : Derby County boss Frank Lampard believes Mason Mount is capable of an England call", "Derby County are set to embark on the dawn of a new era under the management of Frank Lampard.", "Derby County have made an improved bid for Brentford winger Florian Jozefzoon as they look to beat Leeds to the", "Stoke City are keen on signing Derby County striker Matej Vydra, Derby County target Mason Mount will sign a new deal at Chelsea before joining the Rams on loan"], "Aston Villa": ["Joe Bryan has undergone a medical and looks set to join Aston Villa in the next few hours", "Tottenham may now turn their attentions to signing Anthony Martial from Manchester United or Bournemouth's Lewis Cook as talks over Aston Villa's Jack Grealish appear to have stalled", "Jack Grealish is very disappointed and disillusioned that Aston Villa are refusing to sell him to Spurs, according to Sky sources", "Aston Villa have signed FC Ingolstadt 'keeper Orjan Nyland for an undisclosed fee. The Norway international has agreed a three-year deal and will wear the No 1 jersey at Villa Park this season", " Leeds United and Middlesbrough hold talks with Aston Villa over Albert Adomah transfer #lufc #leedsunitedfc"], "Liverpool":["Liverpool misfit Lazar Markovic looks set to finally leave the club", "Liverpool could be set to finally offload misfit Lazar Markovic", "Sheyi Ojo signs new Liverpool deal before loan move to Stade Reims", "Liverpool news: Sadio Mane reveals Man Utd transfer failed after Louis van Gaal talks", "Celtic are keen on signing midfielder Pedro Chirivella from Liverpool", "Galatasaray have made a loan offer to Liverpool for Marko Grujic"], "Villarreal":["Middlesbrough are considering a move for Villarreal midfielder Alfred", "Torino sign Roberto Soriano from Villarreal on loan for one season for", "AC Milan have also agreed for Carlos Bacca and Gianluca Lapadula to join Villarreal and Genoa respectively", "Milan are reportedly on the verge of agreeing a fee for Villarreal winger Samu Castillejo", "Valencia have completed the season-long loan signing of midfielder Denis Cheryshev from La Liga rivals Villarreal"], "West Ham":["Marlon, who had previously attracted attention from Sunderland and West Ham too", "West Ham midfielder Edimilson Fernandes: I want Fiorentina stay", "Moussa Marega must apologise to teammates after failed West Ham move", "West Ham have confirmed the signing of Carlos Sanchez from Fiorentina on a two-year deal", " The Mail Online has it that the Toffees are hoping to prise the Portugal international out of the clutches of West Ham United before the English transfer window closes", "West Ham have completed the signing of Lucas Perez from Arsenal for 4m on a three-year deal"], "Huddersfield":["Huddersfield are interested in signing Montpellier winger Isaac Mbenza, according to Sky sources", "Confirmed: Isaac Mbenza to Huddersfield confirmed", "Stoke City's Eric Maxim Choupo-Moting turns down Huddersfield Town transfer", " Bradford to land Huddersfield midfielder Lewis O'Brien on loan", "Chelsea midfielder Izzy Brown on a season-long loan deal.The 21-year-old spent time on loan at Huddersfield Town"], "Leicester":["Leicester are prepared to make Harry Maguire one of the highest paid players at the club in order to fend off interest from other clubs He signed a five year contract last summer but his outstanding performances at the World Cup have made him a transfer target for other clubs", "Manchester City winger Patrick Roberts is heading to Leicester in a 10m deal, according to the Sunday Mirror.", "Transfer news: Marko Pjaca would be a phenomenal signing for Leicester", "Jose Mourinho takes swipe at transfer failures after win over Leicester", "DEAL DONE Leicester City have announced the signing of Filip Benkovic from Dinamo Zagreb for a reported fee", "Andy King could leave Leicester on loan today", "DEAL DONE Birmingham City have signed Cardiff City striker Omar Bogle on loan", "Cardiff goalkeeper Lee Camp is at Birmingham City's training ground to finalise a loan move to the club", "Birmingham City are interested in signing Aston Villa midfielder Gary Gardner on loan", "DEAL DONE Birmingham City have signed Cardiff City striker Omar Bogle on loan", "Cardiff goalkeeper Lee Camp is at Birmingham City's training ground to finalise a loan move to the club", "Tammy Abraham could still be heading out of Chelsea, with Birmingham Live revealing that he remains a top target for Aston Villa", "Millwall and Birmingham City are lining up moves for goalkeeper Ben Amos from Championship rivals Bolton Wanderers"], "Barca":["Barcelona have confirmed the signing of Arturo Vidal on a three-year deal from Bayern Munich. The midfielder is now set to undergo a medical with Barca in the coming days.", "The midfielder's contract at PSG expires next season but Barca hope that the 23-year-old will force a move, thus rebuffing efforts from the French club to keep him.", "Leicester City have also been linked with the forward, but is unknown which club has lodged a 30 million for Alcacer which has been accepted by Barca.", "Juventus have announced the signing of 16-year-old starlet Pablo Moreno from Barcelona. The Spanish striker arrives after scoring more than 200 goals for Barca's various youth teams at the famed La Masia academy", "Pogba set to secure huge Man Utd bonus despite wanting Barca move"], "Bournemouth":["DEAL DONE Cardiff City have completed a loan deal for Bournemouth midfielder Harry Arter", "DEAL DONE : Hibernian have announced the signing of midfielder Emerson Hyndman on loan from Bournemouth until January", "Transfer news: Should Bournemouth's Jack Simpson now be pushing for Rangers move", "DEAL DONE Bournemouth have completed the signing Colombia international Jefferson Lerma for a club record fee from Levante", "Oldham Athletic are set to sign highly-rated Bournemouth striker Sam Surridge on loan", "Bournemouth have agreed a four-year deal with Leganes for full-back Diego Rico", "Cardiff have announced the season-long loan signing of Harry Arter from Bournemouth"], "Burnley":["Sam Clucas may have found his next club with Stoke having a bid accepted from Swansea He was in talks with Wolves but these have broken down, and a previous 8m deal with Burnley", "Burnley's Dunne joins Hearts on loan", "Burnley are in talks to sign Matej Vydra permanently from Derby County, with Nahki Wells moving in the other direction on loan", "Burnley complete the signing of goalkeeper Joe Hart from Manchester City on initial two-year deal", "Burnley want to sign Mbia on a free transfer", "Burnley are among the clubs to have expressed an interest in signing Nathaniel Mendez-Laing from Premier League newcomers Cardiff", "West Brom open to signing Burnley's Sam Vokes as part of deal for Jay Rodriguez"], "Derby":["Confirmed: Martyn Waghorn to Derby confirmed", "Derby County are interested in signing Bobby Reid from Bristol City", "Report: Derby in talks to let Tom Huddlestone join Gary Rowett at Stoke", "Transfer news: Derby County fans react after Luke Thomas joins Coventry City on loan", "Derby County youngster Luke Thomas set for Coventry City loan", "Brentford have accepted an offer from Derby County for Florian Jozefzoon"], "Swansea":["West Bromwich Albion, Stoke City and Swansea City are all interested in signing Leicester City midfielder Daniel Amartel", "Newcastle have completed the signing of centre-back Federico Fernandez from Swansea City", "Here's Jordan Ayew in his new Crystal Palace shirt after moving to Selhurst Park on a season-long loan deal from Swansea", "Sam Clucas may have found his next club with Stoke having a bid accepted from Swansea", "Swansea City striker Oli McBurnie is no longer a target for Leeds United"], "Celtic":["Tottenham Eye 10m Move for Celtic Star After Scottish Side Miss Out on Champions League", "Transfer news: Celtic should move for Reading's Liam Moore after reported transfer request", "Herrera previously played on loan there when Pedro Caixinha was manager of Santos, who have a partnership arrangement with Celtic", "Celtic's reported summer target Cristiano Piccini slammed after Valencia bow", "Celtic transfer news: Moussa Dembele stance on Lyon and Marseille moves revealed", "Transfer news: Celtic signing Emilio Izaguirre says he had MLS interest this summer"], "Barnsley":["DEAL DONE Hibernian have completed the signing of Barnsley's Stevie Mallan for an undisclosed fee", "Millwall are closing in on the signing of Barnsley and Wales striker Tom Bradshaw", "Transfer news: Millwall make new bid for Barnsley's Bradshaw", "Transfer news: Millwall close on Barnsley star Bradshaw", "Report: QPR set to move for Barnsley's Liam Lindsay", "Millwall make new bid for Barnsley's Bradshaw", "Transfer news: Goalkeeper Walton set for new Barnsley deal", "Millwall have launched a new bid for Barnsley striker Tom Bradshaw as they look to land him before the close of the transfer window next week"],"Ipswich":["Derby have matched Middlesbrough 5m bid for Ipswich striker Martyn Waghorn and are now favourites.", "Jonathan Walters Close To Ipswich Return On Loan Deal", "Ipswich Town are close to securing a loan deal for Jonathan Walters from Burnley,", "Ipswich Town are set to sign Cardiff City striker Omar Bogle on loan", "Ipswich Town & Preston North End are interested in signing Exeter City striker Jayden Stockley", "Ipswich Town are the Championship club to agree a fee with Peterborough for Gwion Edwards", "Birmingham City are thought to be weighing up a move for Ipswich Town goalkeeper Bartosz Bialkowski"],"Ipswich Town":["Derby have matched Middlesbrough 5m bid for Ipswich striker Martyn Waghorn and are now favourites.", "Jonathan Walters Close To Ipswich Return On Loan Deal", "Ipswich Town are close to securing a loan deal for Jonathan Walters from Burnley,", "Ipswich Town are set to sign Cardiff City striker Omar Bogle on loan", "Ipswich Town & Preston North End are interested in signing Exeter City striker Jayden Stockley", "Ipswich Town are the Championship club to agree a fee with Peterborough for Gwion Edwards", "Birmingham City are thought to be weighing up a move for Ipswich Town goalkeeper Bartosz Bialkowski"], "Fulham":["DEAL DONE Tim Ream has agreed a new two-year deal with Fulham", "DEAL DONE Scunthorpe United have signed Fulham striker Stephen Humphrys on loan", "Transfer news: West Ham missed out on brilliant signing as Fulham land Zambo Anguissa", "Fulham expect to be able to complete the signing of Newcastle United striker Aleksandar Mitrovic when the Serbia international returns from holiday", " Three clubs make contact with Fulham over Rui Fonte signing", "ulham have announced the signing of Atletico Madrid striker Luciano Vietto on a season-long loan"],"MK Dons":["Transfer news: Chase on for MK Dons ace Chuks Aneke", "DEAL DONE MK Dons have signed defender Mathieu Baudry on a free transfer", "Transfer news: MK Dons and Mansfield battle for former Luton midfielder D'Ath", "DEAL DONE MK Dons have completed the signing of goalkeeper Stuart Moore", "Transfer news: Chase on for MK Dons ace Chuks Aneke", "Transfer news: MK Dons and Mansfield battle for former Luton midfielder D'Ath"],"Fleetwood":["Fleetwood agree Evans loan deal", "Swindon to snap up Fleetwood's Diagouraga", "Fleetwood move for Wigan's Craig Morgan", "Transfer news: Fleetwood weigh up move for former Norwich midfielder Wes Hoolahan", "Confirmed: Fleetwood complete deal for James Husband", "Confirmed: Fleetwood complete deal for Paul Jones", "Confirmed: Lewie Coyle to Fleetwood confirmed"],"Millwall":["Wolves winger Ben Marshall reportedly prefers Millwall move", "Middlesbrough enter talks with Millwall about signing George Saville", "Millwall have launched a new bid for Barnsley striker Tom Bradshaw as they look to land him before the close of the transfer window next week", "Confirmed: Millwall complete deal for Tom Bradshaw", "Transfer news: Wolves winger Ben Marshall reportedly prefers Millwall move"],"Crystal Palace":["Crystal Palace looking to sign Sassuolo forward Khouma Babacar?", "Roy Hodgson Insists Crystal Palace Winger & Everton Target Wilfried Zaha Is Not for Sale", "Transfer news: Crystal Palace's Andros Townsend would be an excellent signing for Burnley", "Report: Crystal Palace targeting Celtic striker Moussa Dembele", " Crystal Palace express interest in signing Chelsea's Tammy Abraham on loan", "Report: Crystal Palace and Southampton in talks with", "Everton enter race to sign Crystal Palace winger Wilfried Zaha", "Newcastle, Crystal Palace target Japan World Cup duo", "Crystal Palace want Ruben Loftus-Cheek return"],"Middlesbrough":["Middlesbrough agree deal for Bristol City defender Aden Flint", " Middlesbrough hoping to sign Millwall's George Saville in", "Report: Middlesbrough confident of signing Crystal Palace's Jason Puncheon", "Mo Besic to Middlesbrough is going to be loan rather than permanent transfer", "DEAL DONE Accrington Stanley have signed goalkeeper Connor Ripley from Middlesbrough on a season-long loan", "Jason Puncheon free to leave Crystal Palace as Middlesbrough chase loan deal", " Middlesbrough agree deals with Everton pair Yannick Bolasie and Mo Besic", "Middlesbrough are trying to bring in Everton midfielder Muhamed Besic on loan, according to Sky sources.", "Middlesbrough are attempting an ambitious move for Everton winger Yannick Bolasie, according to Sky sources.", " Yannick Bolasie travels for Middlesbrough medical ahead of Everton exit"], "Scunthorpe":["DEAL DONE Scunthorpe United have signed Fulham striker Stephen Humphrys on loan", "Official: Ike Ugbo joins Scunthorpe on loan until January", "Jak Alnwick agrees to join ex-Rangers pair at Scunthorpe United after Steven Gerrard sanctions exit", "Derby County and Rotherham United are interested in signing Scunthorpe United winger Duane Holmes", "Chelsea ready to send Ike Ugbo to Scunthorpe", "Chelsea ready to send Ike Ugbo to Scunthorpe"],"Sunderland":["Report: Sunderland's Connor Shields set to join Alloa on season-long loan deal", "OPINION: Sunderland are still in the market for NEW players - here are FIVE we could target", "Turkish giants Besiktas are interested in signing Sunderland defender Papy Djilobodji", "Sunderland's Papy Djilobodji agrees personal terms with Trabzonspor"],"Bolton":["Confirmed: Joseph Michael Williams to Bolton confirmed", "DEAL DONE Bolton Wanderers have completed the signing of midfielder Gary", "Bolton in talks with Derby County to sign David Nugent", "Confirmed: Bolton complete deal for Remi Luke Matthews", "Bolton Wanderers are trying to sign Bradford City target man Charlie Wyke and former Burton Albion midfielder Hope Akpan", "Former Bolton Wanderers midfielder Jem Karacan is in talks with Oxford United", "Millwall and Birmingham City are lining up moves for goalkeeper Ben Amos from Championship rivals Bolton Wanderers", "Bolton Wanderers are close to signing Pawel Olikowski on a free transfer"],"Wigan":["Wigan Athletic are chasing Leicester City defender Callum Elder after he impressed during a loan spell at the DW Stadium last season", "Transfer news: Callum Lang agrees new Wigan deal and joins Oldham on loan", "Confirmed: Wigan complete deal for Lee Evans", "Wigan are eyeing up a move for Arsenal left-back Marc Bola", "'Confirmed: Wigan complete deal for Dan Burn", "Aston Villa boss Steve Bruce has convinced the clubs investors to push through a bid to sign star Wigan"],"Leeds":["Report: Leeds contact West Ham about signing Domingos Quina", "Leeds United in battle for River Plate's Augusto Batalla", "Middlesbrough set to beat Leeds for Everton Midfielder Muhamed", "Leeds should make late bid to hijack Middlesbrough's reported George Saville move", "Leeds United Caleb Ekuban in talks over Trabzonspor move"], "Wolves":["Wolves defender Kortney Hause closing in on a loan move to Reading", "Wolves are now very close to signing Adama Traore in a club record deal", "Wolves are looking to make a move for Croatian World Cup star Domagoj Vida", "Everton boss Marco Silvas transfer comments potential boost for Wolves", "West Brom are weighing up a move for Wolves defender Danny Batth", "Wolves are set to break their transfer record to sign Middlesbrough winger Adama Traore", "Transfer news: Wolves re-signing Bakary Sako is looking increasingly like a good idea", "Wolves proposed move for Manchester City defender Oleksander Zinchenko has fallen through"], "Blackburn":["Bradley Dack has agreed a new deal at Blackburn Rovers", "Blackburn Rovers have agreed a deal with Newcastle United for striker Adam Armstrong. The 21-year-old was on loan at Ewood Park last season and is expected to cost newly-promoted Blackburn", "Manchester City striker Lukas Nmecha now can count West Brom among the suitors to take him on loan this season, reports the Daily Mail. The youngster has impressed on City's pre-season tour and already has an offer from Swansea City, with Blackburn also interested", "The midfielder previously had a spells at Blackburn"], "Arsenal": ["Fenerbahce move would be a 'backwards step' for Jack Wilshere, says former Arsenal midfielder Adrian Clarke: Jack Wilshere has been urged not to join Fenerbahce this summer, as he would be taking a 'backwards step' in his career. Latest reports c", "Liverpool are keen on signing Arsenal midfielder Aaron Ramsey", "Arsenal boss Unai Emery is plotting a 25m move for Croatian defender", "Arsenal striker Lucas Perez has undergone a medical at West Ham", "Fulham sign Arsenal defender Calum Chambers on season-long loan", "Barcelona Transfer News: Ousmane Dembele Rules out Exit Amid Arsenal Rumours"], "Nacer Chadli": ["Transfer news: Everton should make move for West Broms Nacer Chadli", "Transfer news: West Brom's Nacer Chadli would be a risky, yet potentially brilliant signing for Newcastle", "Confirmed: Monaco complete deal for Nacer Chadli"], "Burton Albion": ["DEAL DONE Scunthorpe United have completed the signing of midfielder Matthew Lund for an undisclosed fee from Burton Albion", "Bolton Wanderers are trying to sign Bradford City target man Charlie Wyke and former Burton Albion midfielder Hope Akpan", "DEAL DONE Scunthorpe United have completed the signing of midfielder Matthew Lund for an undisclosed fee from Burton Albion", "Bolton Wanderers are trying to sign Bradford City target man Charlie Wyke and former Burton Albion midfielder Hope Akpan"]}


if __name__ == '__main__':
    main()
