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
import spacy
from spacy.util import minibatch, compounding

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
transferdb = myclient["transferdb"]



def main():
    # get_entities(unicode("Benik Afobe hits out at 'disrespectful' Wolves over Stoke City transfe"))
    #
    # nltk_method("Reading are interested in signing Barnsley defender Andy Yiadom on a free transfer #ReadingFC #BarnsleyFC pic.twitter.com/K45MEvqJvI,,,#ReadingFC")
    # filter_pfalse()
    # ex= ["Fenerbahce move would be a 'backwards step' for Jack Wilshere, says former Arsenal midfielder Adrian Clarke: Jack Wilshere has been urged not to join Fenerbahce this summer, as he would be taking a 'backwards step' in his career. Latest reports c", "Liverpool are keen on signing Arsenal midfielder Aaron Ramsey", "Arsenal boss Unai Emery is plotting a 25m move for Croatian defender", "Arsenal striker Lucas Perez has undergone a medical at West Ham", "Fulham sign Arsenal defender Calum Chambers on season-long loan", "Barcelona Transfer News: Ousmane Dembele Rules out Exit Amid Arsenal Rumours"]

    # retrain_nlp_model(unicode("Arsenal",encoding="utf-8"), ex)
    retrain_batch(retrain_data)
    # process_tweet()


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
            df_pfalse = df_pfalse.drop(df_pfalse.index[i])
    df_pfalse.to_csv("info/filtered_pfalse.csv", encoding='utf-8', sep=';')
    print(len(df_pfalse.index))



def transfer_talk_check(text):

    if(isinstance(text, basestring)):
        if ("transfer" in text) or ("medical" in text) or ("signing" in text) or ("verge" in text) or ("complete" in text) or ("accepted" in text) or ("transfer news" in text) or ("in talks" in text) or ("arrived" in text) or ("move" in text) or ("loan" in text) or ("agree" in text) or ("target" in text) or ("transfer window" in text) ("re-signed" in text):
            return True
        else:
            return False


def process_tweet():
    # CHECK DELIMETER
    df_transfer_true = pd.read_csv("info/filtered_pfalse.csv", sep=';', error_bad_lines=False, encoding="utf-8")
    df_transfer_true = df_transfer_true.drop(df_transfer_true.index[0:35523])
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
    if ("rejected" in text) or ("injury" in text) or ("turned down" in text) or ("XI" in text) or ("kit" in text) or ("renewed" in text) or ("renew" in text) or ("extension" in text) or ("more years" in text) or ("not interested" in text) or ("appointed manager" in text) or ("Highlights" in text) or ("All Goals" in text) or ("Friendly" in text) or ("FT" in text)  or ("appearance" in text):
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
        start = i.index(entity)
        end = start+len(entity)
        entry = (unicode(i.decode('utf-8')), {'entities': [(start, end, 'ORG')]})
        TRAIN_DATA.append(entry)

     # """Load the model, set up the pipeline and train the entity recognizer."""
    nlp = spacy.load(output_dir)  # load existing spaCy model
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

retrain_data = {"Liverpool":["Manchester City shot-stopper Joe Hart nutmegs Mohamed Salah with a backheel during Liverpool friendly, Liverpool transfer news: Jurgen Klopp defends £67million Alisson fee","Liverpool news: Jurgen Klopp says Xherdan Shaqiri's performance against Manchester United was 'not normal': Liverpool boss Jurgen Klopp described Xherdan Shaqiri’s debut performance", "Woodburn set to join Sheffield United on loan from Liverpool #epl : The youngster is wanted by the Championship", "New Liverpool signing Xherdan Shaqiri responds to criticism over his ‘poor attitude’ at Stoke City"], "Villareal":["Santi Cazorla: former Arsenal star on the comeback trail at Villarreal", "DEAL DONE Ramiro Funes Mori has joined Villarreal on a four-year contract from Everton", "DONE DEAL : Villarreal have completed the signing of Santi Cazorla on a free transfer from Arsenal #Arsenal #Villarreal", "Former Arsenal favourite Santi Cazorla grateful to Villarreal #epl : Santi Cazorla thanks Villarreal for giving him a chance to restart his career in Spain following a long-term injury layoff."], "Huddersfield":["Confirmed: Huddersfield complete deal for Adama Diakhaby", "Huddersfield boss Wagner warns Stoke to get serious about Ince #epl : Stoke City are chasing Huddersfield Town winger Thomas Ince", "Huddersfield on the verge of signing Monaco striker Adama Diakhaby – reports", "Chelsea are signing veteran goalkeeper Robert Green in a shock free transfer move. The former England international is heading to Stamford Bridge to join as cover after a year spent on the Huddersfield Town bench"], "West Ham":["Transfer news: Have Liverpool made an error over reportedly imminent £35m West Ham new boy Felipe Anderson", "Jack Wilshere blasted by Adrian Durham for ‘appalling’ move from Arsenal to West Ham United", "Transfer news: Surely West Ham won't sign Celtic's Olivier Ntcham if Camacho happens", "West Ham are trying to sign Arsenal forward Lucas Perez", "overtake them at the top of the First Division with a 3–1 away win over relegation-threatened West Ham United"], "Leicester":["Leicester City are understood to be among the clubs interested in Gary Cahill.", "Leicester City have enquired about Everton winger Yannick Bolasie", "Claude Puel insists Leicester have not received any offers for goalkeeper Kasper Schmeichel", "BREAKING: Manchester United have approach Leicester City over the sale of Harry Maguire"], "Birmingham":["Birmingham have swooped in ahead of Ipswich to land Cardiff’s Omar Bogle on loan", "Done deal: Birmingham City confirm goalkeeper signing", "Millwall and Birmingham City are lining up moves for goalkeeper Ben Amos from Championship rivals Bolton Wanderers", "Birmingham City are set to make an improved bid for Ipswich Town goalkeeper Bartosz Bialkowski after seeing their first offer rejected", "Birmingham City are thought to be weighing up a move for Ipswich Town goalkeeper Bartosz Bialkowski"], "Barca":["Transfer news LIVE: Kepa to Chelsea, Man Utd agree deal, Pogba to Barca, Arsenal latest", "The midfielder is now set to undergo a medical with Barca in the coming days", "Arturo Vidal as a Barcelona player I am really happy to be at Barca", "but is unknown which club has lodged a €30 million (£26.7m/$35m) for Alcacer which has been accepted by Barca"], "Spurs":["Tottenham legend Chris Hughton praises Spurs for building new stadium in same place as White Hart", "Wenger took this sly dig at local rivals Spurs", "It is understood discussions are now ongoing with Spurs keen to include an obligation to buy clause", "At the moment, Spurs haven’t got anywhere near what the owners want to even consider, so there’s not a discussion to be had", "Spurs are now also plotting a swoop"], "Bournemouth":["Sheffield United boss Chris Wilder wants to spend his windfall from David Brooks’ sale to Bournemouth on Southampton hitman Sam Gallagher", "DEAL DONE Bournemouth have signed highly-rated youngster David Brooks from Sheffield United for £12m", "Wigan Athletic are set to sign AFC Bournemouth midfielder Emerson Hyndman on loan", "Tottenham are plotting a £30m swoop for Bournemouth midfielder Lewis Cook.", "Bournemouth set to sign Leganes left-back Diego Rico in £10.7m transf", "Bournemouth left-back Brad Smith has joined Seattle Sounders on loan until June.", "Tottenham may now turn their attentions to signing Anthony Martial from Manchester United or Bournemouth's Lewis Cook as talks over Aston Villa's Jack Grealish"], "Burnley":["Burnley have signed Derby striker Matej Vydra on a three year contract with the option of another year", "Leicester 'keeper Kasper Schmeichel has hit out at the exceptionally harsh treatment of new Burnley signing Joe Hart", "Burnley are in talks to sign Matej Vydra permanently from Derby County", "Joe Hart has left Manchester City to join Burnley on an initial two-year deal. The England international has brought a", "Burnley complete the signing of goalkeeper Joe Hart from Manchester City on initial two-year deal", "And now a move to Turkey is on the cards, with Burnley - who were previously keen on Forster - having opted to sign Joe Hart instead", "Ben Mee signed a new three-year contract with Burnley last night", "DEAL DONE Burnley have completed the signing of Derby County striker Matej Vydra", "Burnley and Derby have agreed a deal that will see the Clarets sign Matej Vydra and Nahki Wells join the Rams"], "Derby":["Cardiff City and Middlesbrough are reported to be interested in signing Derby County midfielder Tom Huddlestone", "Matej Vydra is now looking set to join Burnley from Derby", "Huddersfield Town defender Scott Malone has joined Derby County for an undisclosed fee", "Burnley have signed Derby striker Matej Vydra on a three year contract with the option of another year", "Schmeichel has hit out at the exceptionally harsh treatment of new Burnley signing Joe Hart, saying people have very short memories"], "Swansea":["Swansea are in talks over a potential deal to sign Yeovil’s Tom James", "Swansea City are interested in Brentford midfielder Ryan Wood", "Blackburn Rovers and Swansea City are both interested in Manchester City striker Lukas Nmecha", "Swansea City are set to sign Nottingham Forest winger Barrie McKay", "BREAKING: Burnley are in talks to sign Swansea defender Alfie Mawson. The Swans want around £20M for the centre-back"], "Celtic":["Report: Fulham make £9m bid for Celtic defender Dedryck Boyata #celtic", "Celtic criticise Rangers' Old Firm ticket cuts for away fans as Scottish Premiership champions call for talks to resolve issue: Celtic have proposed the idea of opening talks between themselves, Rangers and Scottish league officials over a ticket", "Everton are reportedly set to put in a £25 million bid for Celtic's Kieran Tierney", "French side Lille are ready to make a £5m bid for Celtic defender Jozo Simunovic", "Dembele grabs his second from the penalty spot and Celtic lead"], "Barnsley":["Barnsley have rejected two six figure bids from two unnamed Championship clubs for striker Kieffer Moore", "DEAL DONE Barnsley have appointed former Hannover 96 boss Daniel Stendel as their new manager", "Barnsley and Hull City are looking to make a move for Ipswich Town midfielder Cole Skuse", "DEAL DONE Bradford City have signed Barnsley striker Tom Clare", "Barnsley have signed midfielder Kenny Dougall from Eredivisie side Sparta Rotterdam for an undisclosed fee on a two-year contract"], "Ipswich Town":["Manchester City have agreed a fee with Ipswich Town for youngster Ben Knight. The 16-year-old forward has already featured for the England.", "Paul Hurst has confirmed that Ipswich Town are close to signing Chelsea defender Trevoh Chalobah on loan.", "Ipswich Town have signed Trevoh Chalobah on-loan from Chelsea until the end of the season Paul Hurst has completed", "helsea defender Trevoh Chalobah set for move to Ipswich Town after new boss Paul Hurst confirms", "Ipswich Town have made a £2m bid for Rangers forward Josh Windass"], "Fulham":["Fulham move to hijack Joe Bryan's £6m switch to Aston Villa", "Bryan has indicated to Villa he would like the chance to play in the Premier League and Fulham improved their offer.", "Fulham move to hijack Joe Bryan's £6m switch to Aston Villa", "rsenal head coach Unai Emery explains decision to loan Calum Chambers to Fulham", "Tony Khan breaks his silence on rumours surrounding Fulham starlet Ryan Sessegnon: Ryan Sessegnon will not be leaving Fulham", "Tottenham offered Fulham Danny Rose in attempt to land Ryan Sessegnon", "talkSPORT exclusive: Alfie Mawson believes Aleksandar Mitrovic will be of huge importance to Fulham this season"], "MK Dons":["DEAL DONE MK Dons have completed the signing of goalkeeper Stuart Moore", "DEAL DONE MK Dons have signed defender Mathieu Baudry on a free transfer", "Transfer news: Chase on for MK Dons ace Chuks Aneke", "DEAL DONE MK Dons have signed attacking midfielder Ryan Harley from Exeter City", "DEAL DONE MK Dons have signed former Luton Town winger Lawson D'Ath", "Transfer news: Former Chelsea youngster Houghton set for MK Dons move", "DEAL DONE MK Dons have signed defender Mathieu Baudry on a free transfer", "Transfer news: Chase on for MK Dons ace Chuks Aneke", "DEAL DONE MK Dons have signed attacking midfielder Ryan Harley from Exeter City"], "Fleetwood Town":["DEAL DONE Fleetwood Town have re-signed Leeds United defender Lewie Coyle on loan", "DEAL DONE Fleetwood Town have signed Wigan Athletic defender Craig Morgan","Swindon Town are closing in on the signing of Fleetwood Town's Toumani Diagouraga", "Fleetwood Town are in advanced talks with Sheffield United ahead of a season-long loan for striker Ched Evans", "Bristol City are taking a close look at signing Fleetwood Town’s Alex Cairns", "DEAL DONE Fleetwood Town have re-signed Leeds United defender Lewie Coyle on loan", " Burnley striker Chris Long has moved to Fleetwood Town.Fleetwood have signed forward Ched Evans"], "Millwall":["11 December 1991 – Millwall receive the go-ahead to relocate to a new 20,000-seat stadium at Bermondsey", "Millwall plan Premier League redevelopment of The Den", "Norwich are set to beat Millwall to the signing of Wolves winger Ben Marshall, according to Sky sources.", "Confirmed: Ben Amos to Millwall confirmed", "Brighton & Hove Albion winger Jiri Skalak set for a move to Millwall"], "Chelsea":["Tammy Abraham set for Chelsea stay and increased role despite interest from Premier League", "The Frenchman only joined Chelsea six months ago but new boss Maurizio Sarri is seemingly allowing him to leave as he looks to strengthen his squad", "Crystal Palace and Southampton want to sign Chelsea midfielder Danny Drinkwater, according to the Daily Mirror. Drinkwater joined the west Londoners", "Chelsea will not resume talks with Real Madrid over a deal for goalkeeper Thibaut Courtois", "Inter will turn their attention to signing either Bayern Munich’s Arturo Vidal or Tiemoue Bakayoko from Chelsea", "Chelsea goalkeeper rumors: Donnarumma-Morata swap; £80m Alisson", "Derby boss Lampard joins scramble for exciting Chelsea"], "Crystal Palace":["Crystal Palace close to signing Cheikhou Kouyaté and Jordan Ayew", "Crystal Palace star Jonny Williams talks future under Roy Hodgson amid", "Crystal Palace transfer news EXCLUSIVE: Eagles eyeing up 'the new Zinedine Zidane", "Max Meyer to Crystal Palace: Who is the Germany international arriving at Selhurst Park on a free transfer", "Crystal Palace set to announce Max Meyer transfer as Roy Hodgson lands second summer deal", "Mamadou Sakho wanted by Lyon for cut-price £13million transfer from Crystal Palace"], "Middlesbrough":["Sheyi Ojo 'eyed for loan move' by Middlesbrough as Championship side ponder swoop for Liverpool youngster", "A FRUSTRATED George Friend has issued a heartfelt apology to fans after Middlesbrough’s hopes of sealing a Premier League return at the", "Middlesbrough and Liverpool in talks over £10m Sheyi Ojo deal", "Middlesbrough are withdrawing Maccarone the Italian, Nemeth the Slovakian, and Stockdale.", " Food for thought after Arsenal fans greeted a 1-1 draw with Middlesbrough with boos, 1998"], "Scunthorp":["Manchester United loaning Cameron Borthwick-Jackson to Scunthorpe", "West Brom have seen an offer accepted for Scunthorpe defender Conor Townsend", "Scunthorpe United are closing in on the signing of Dover Athletic winger Mitchell Pinnock", "Confirmed: Scunthorpe complete deal for James Horsfield"], "Sunderland":["Report: Sunderland's Mohamed Eisa bid £500,000 short of Cheltenham's valuation #sunderlandafc", "Sunderland transfer news: Five most likely signings", "Sunderland have agreed a fee to sign Peterborough United defender Jack Baldwin", "DEAL DONE Sunderland have completed the signing of former Sheffield Wednesday defender Glenn Loovens", "DEAL DONE St Etienne have signed winger Wahbi Khazri from Sunderland for £6m on a four-year deal", "Sunderland are hoping to complete a £1.6m double deal for strikers Mohamed Eisa and Charlie Wyke after tabling formal offers for the duo tonight"], "Bolton":["Confirmed: Josh Magennis to Bolton confirmed", "Bolton Wanderers are trying to sign Bradford City target man Charlie Wyke and former Burton Albion midfielder Hope Akpan", "Sunderland and Bolton have both made enquiries for Peterborough captain Jack Baldwin.", "Bolton are in talks to sign Erhun Oztumer from Walsall", "Bolton Wanderers are targeting a move for Leicester City left-back Callum Elder"], "Wigan":["Wigan are closing in on the signing of Everton defender Antonee Robinson on loan", "Callum Connolly will join Wigan Athletic on a season-long loan from Everton", "Wigan Athletic midfielder Jordan Flores is poised to join Swedish club Ostersunds on loan", "Aston Villa are set to make a bid worth £5m for Wigan Athletic’s Nick Powell", "Transfer news: Wigan midfielder Flores set for Ostersunds loan #wiganathleticfc", "Confirmed: Wigan complete deal for Cédric Kipré"], "Leeds":["Leeds United sign striker Rod Wallace from Southampton for £1.6million and defender Tony Dorigo from Chelsea for £1.3million", " Leeds United 3-1 Stoke City: Marcelo Bielsa off to winning start in Championship with scintillating victory over Potters: Marcelo Bielsa", "Leeds midfielder Ronaldo Vieira has arrived in Italy to complete his move to Sampdoria", "Leeds have signed Patrick Bamford from fellow Championship side Middlesbrough on a four-year deal for a fee of £7m", "Leeds have signed England U21 winger Jack Harrison on a season-long loan from Manchester City.", "Transfer news: Are Leeds United's main competitors about to bow out of Matthew Pennington pursuit?", "Report: Jerry Mbakogu to rescind Carpi contract after Leeds failed to activate £3.5m agreement"], "Blackburn Rovers":["Alan Shearer scored 16 goals in his first 21 Premier League games for Blackburn Rovers before a serious knee injury ended his season", "Bradley Dack has agreed a new deal at Blackburn Rovers", "Blackburn Rovers have agreed a deal with Newcastle United for striker Adam Armstrong", "Transfer news: Blackburn Rovers keen to reward Ryan Nyambe with new deal", "DEAL DONE Accrington Stanley have signed Blackburn Rovers defender Matthew Platt on a season-long loan", "Bill Fox, president of the Football League and chairman of Blackburn Rovers, dies after a short illness at the age of 63"], "Wolves":["Adama Traoré joins Wolves from Middlesbrough for club-record £18m", "Wolves are set to break their transfer record to sign Middlesbrough winger Adama Traore for £18 million", "Manchester United defender Chris Smalling has agreed a deal with Wolves, according to reports in the Daily Express", "Newly-promoted Wolves are looking to make another high-profile signing this summer by bringing in defender Pepe from Besiktas", "Report explains how Goncalo Guedes feels about potential Wolves move"], "Bradford":["Confirmed: Bradford complete deal for Eoin Doyle", "Transfer news: Doncaster to sign former Bradford striker Paul Taylor", "DEAL DONE Lincoln City have completed the signing of Bradford City forward Shay McCartan", "DEAL DONE Romain Vincelot has joined Crawley Town on a two-year deal from Bradford City", "Huddersfield Town winger Sean Scannell is in talks with Bradford City over a potential move to the League One club", "Sunderland have made a bid for Bradford City striker Charlie Wyke"], "Accrington":["DEAL DONE Accrington Stanley have re-signed Cambridge United midfielder Piero Mingoia", "Neville and Accrington owner in Twitter row over Salford 'stealing' league place", "Accrington Stanley are in talks with in-demand striker Kayden Jackson over a new contract to keep the striker at the club", "DEAL DONE Accrington Stanley have re-signed Cambridge United midfielder Piero Mingoia", "DEAL DONE Accrington Stanley have signed Northern Irish teenager Andrew Scott on a three-year deal"]}

if __name__ == '__main__':
    main()
