import pymongo
from pymongo import MongoClient
import pandas as pd
from pprint import pprint
# import urllib2
from bs4 import BeautifulSoup
import csv
from bson.objectid import ObjectId

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
transferdb = myclient["transferdb"]

def main():
    # store_syn_false("info/synres_extras7.csv")
    clubs = transferdb["english_clubs"]

    # coll_list=transferdb.list_collection_names()
    # print(coll_list)
    # coll = transferdb["labelled_false_2015"]
    curs = clubs.find({})
    for doc in curs:
            pprint(doc)
    # print(true.count())
    # print(true.count())
    # # store_syn_false("info/synres.csv")
    # print(false.count())


def merge_db(namekeep, namecol):
    coll = transferdb[namecol]
    collkeep = transferdb[namekeep]
    df = pd.DataFrame(list(coll.find()))

    for i, row in df.iterrows():
        entry = entry = {"username": row['username'], "tweet_text": row["tweet_text"], "label":row["label"]}
        collkeep.insert_one(entry)


def correct_db(name, idlist):
    coll = transferdb[name]
    for i in idlist:
        coll.delete_one({"_id": ObjectId(i)})


def synonym_db():
    transferdb = myclient["transferdb"]
    clubcoll = transferdb["clubs"]
    syncoll = transferdb["club_syns"]
    df = pd.DataFrame(list(clubcoll.find()))
    for index, row in df.iterrows():
        entry = {"club": row["Name"], "syns": generate_syns(row["Name"])}
        syncoll.insert_one(entry)
    manual_clubs


def make_english_clubs(qPage):
    col = transferdb["english_clubs"]
    quote_page = qPage
    page = urllib2.urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')
    ar =  soup.find_all("tbody")
    window = 0
    for i in range(2, 26):
        tables = ar[i].text.strip()
        clubs = tables.split('\n\n')
        for i in clubs:
            list = i.split('\n')
            if len(list)>1:
                if int(list[3])<5:
                    syns = generate_syns(list[1])
                    [x.encode('utf-8') for x in syns]
                    nicks = syns+[list[4].encode('utf-8')]
                    entry = {"Name": list[1], "League": list[3], "syns": nicks}
                    col.insert_one(entry)
                    # print(entry)

def generate_syns(club):
    components = club.split(" ")
    syns = []
    for i in components:
        if (i is not "FC") or (i is not "AFC") or (i is not "Town"):
            syns.append(i)
    return syns

def store_data(transferdb, path):
    mycol = transferdb["true_test_transfers"]
    df_transfer_true = pd.read_csv(path, sep=';', error_bad_lines=False, encoding="utf-8")
    for i, row in df_transfer_true.iterrows():
        print(i)
        entry = {"username": row['username'].strip(), "date": row['date'].strip(), "tweet_text": row['text'].strip(), "label":"True"}
        mycol.insert_one(entry)
    return

def store_syn_false(path):
    coll = transferdb["synfalse_test_transfers"]
    df_transfer_synfalse = pd.read_csv(path, sep=';', error_bad_lines=False, encoding="utf-8")
    for i, row in df_transfer_synfalse.iterrows():
        if len(row.text)>6:
            print(i)
            print(row["date"])
            entry = {"username": row['username'].strip(), "date": row['date'].strip(), "tweet_text": row['text'].strip(), "label":"False"}
            coll.insert_one(entry)
    return


def make_player_db(transferdb, path):
    coll = transferdb["players"]
    df_transfer_true = pd.read_csv(path, sep=',', error_bad_lines=False, encoding="utf-8")
    for i, row in df_transfer_true.iterrows():
        entry = {"player": row['Name'].strip(), "date": row["Date"], "label": "True"}
        coll.insert_one(entry)
    return


def make_club_db(transferdb, path):
    coll = transferdb["clubs"]
    df_transfer_true = pd.read_csv(path, sep=',', error_bad_lines=False, encoding="utf-8")
    for i, row in df_transfer_true.iterrows():
        entry1 = {"Name": row["Moving from"].strip()}
        entry2 = {"Name": row["Moving to"].strip()}
        coll.insert_one(entry1)
        coll.insert_one(entry2)
    return

def make_club_dbt(entry):
    coll = transferdb["clubs"]
    coll.insert_one(entry)


def make_transfer_db(transferdb, path):
    coll = transferdb["confirmed_transfers_2017"]
    df_transfer_true = pd.read_csv(path, sep=',', error_bad_lines=False, encoding="utf-8")
    for i, row in df_transfer_true.iterrows():
        entry = {"Date": row["Date"].strip(),"Name": row["Name"].strip(),"Moving from": row["Moving from"].strip(),"Moving to": row["Moving to"].strip(), "happened": True}
        coll.insert_one(entry)
    return


def query_collection(query, cname, db):
    collection=db[cname]
    docs = collection.find(query)
    # print("Query: "+ query["label"])
    return docs


def reset_collections(transferdb):
    coll_list=transferdb.list_collection_names()
    print(coll_list)
    for i in coll_list:
        coll = transferdb[i]
        coll.drop()
    coll_list=transferdb.list_collection_names()
    print(coll_list)
    path = "info/true_data_set.csv"
    path2 = "info/transfers2017.csv"
    store_data(transferdb, path)
    make_player_db(transferdb, path2)
    make_transfer_db(transferdb, path2)
    make_player_db(transferdb, path2)
    make_club_db(transferdb, path2)
    make_english_clubs("https://en.wikipedia.org/wiki/List_of_football_clubs_in_England")
    synonym_db()
    coll_list=transferdb.list_collection_names()
    print(coll_list)


def manually_add_club(transferdb, club, val):
    coll = transferdb["club_syns"]
    query = {"club": club}

    entry = coll.find_one(query)
    # new_entry = [entry["syns"]].append(val)
    upval = {"$set": {"syns": val}}
    print("BEFORE: ")
    print(entry)
    coll.update_one(query, upval, upsert=False)
    list = coll.find_one(query)
    print("AFTER: ")
    print(list)

def manual_clubs(transferdb):
    coll = transferdb["clubs"]
    entry1 = {"Name": "Tottenham", "syns":"Spurs"}
    entry2 = {"Name": "Tottenham Hotspur", "syns":"Spurs"}
    entry3 = {"Name": "Barcelona", "syns":"Barca"}
    entry4 = {"Name": "Milton Keynes Dons", "syns":"MK Dons"}
    entry4 = {"Name": "Fleetwood Town", "syns":"Fleetwood"}
    entry4 = {"Name": "Wolverhampton Wanderers", "syns":"Wolves"}

    coll.insert_one(entry1)
    coll.insert_one(entry2)
    coll.insert_one(entry3)
    coll.insert_one(entry4)

def write_to_csv(cname, fname):
    coll = transferdb[cname]
    file = open(fname,'w')
    curs = coll.find({})
    for doc in curs:
        line = doc['username'] + ";"+ (doc['date']) + ";"+ doc['tweet_text'] + ";"+ doc["label"]
        file.write(line+"\n")
    file.close()



def intersect_db():
    coll = transferdb["labelled__false_tweets"]
    curs = coll.find({})
    collnew = transferdb["labelled__false_querys"]
    for doc in curs:
            query = {'tweet_text': doc['tweet_text']}
            collnew.delete_one(query)

if __name__ == '__main__':
    main()
