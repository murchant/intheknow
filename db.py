import pymongo
from pymongo import MongoClient
import pandas as pd
from pprint import pprint

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

def main():

    transferdb = myclient["transferdb"]
    # DATABASE SETUP
    # path = "info/true_data_set.csv"
    # path2 = "info/transfers2018.csv"
    # store_data(transferdb, path)
    # make_player_db(transferdb, path2)
    # make_transfer_db(transferdb, path2)
    # make_player_db(transferdb, path2)
    # # reset_collections(transferdb)
    # make_club_db(transferdb, path2)
    # synonym_db()
    coll = transferdb["labelled__false_tweets"]
    curs = coll.find({})
    for doc in curs:
        pprint(doc)
    print(coll.count())
    # coll_list=transferdb.list_collection_names()
    # print(coll_list)
    # coll = transferdb["club_syns"]
    # df = pd.DataFrame(list(coll.find()))
    # for i, row in df.iterrows():
    #     print(row["syns"])



def synonym_db():
    transferdb = myclient["transferdb"]
    clubcoll = transferdb["clubs"]
    syncoll = transferdb["club_syns"]
    df = pd.DataFrame(list(clubcoll.find()))

    for index, row in df.iterrows():
        entry = {"club": row["Name"], "syns": generate_syns(row["Name"])}
        syncoll.insert_one(entry)

# Generate club synonyms by simply rearranging their official name

def generate_syns(club):
    components = club.split(" ")
    syns = []
    for i in components:
        if (i is not "FC") or (i is not "AFC") or (i is not "Town"):
            syns.append(i)
    return syns

def store_data(transferdb, path):
    mycol = transferdb["true_transfers"]
    df_transfer_true = pd.read_csv(path, sep=',', error_bad_lines=False, encoding="utf-8")
    for i, row in df_transfer_true.iterrows():
        entry = {"username": row['username'].strip(), "date": row['date'].strip(), "text": row['text'].strip()}
        mycol.insert_one(entry)
    return


def make_player_db(transferdb, path):
    coll = transferdb["players"]
    df_transfer_true = pd.read_csv(path, sep=',', error_bad_lines=False, encoding="utf-8")
    for i, row in df_transfer_true.iterrows():
        entry = {"player": row['Name'].strip(), "date": row["Date"]}
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


def make_transfer_db(transferdb, path):
    coll = transferdb["confirmed_transfers"]
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
    path2 = "info/transfers2018.csv"
    store_data(transferdb, path)
    make_player_db(transferdb, path2)
    make_transfer_db(transferdb, path2)
    coll_list=transferdb.list_collection_names()
    print(coll_list)


if __name__ == '__main__':
    main()
