import pymongo
from pymongo import MongoClient
import pandas as pd
from pprint import pprint

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

def main():
    transferdb = myclient["transferdb"]
    # coll = transferdb["clubs"]
    # entry1 = {"Name": "Tottenham", "syns":"Spurs"}
    # coll.insert_one(entry1)
    # reset_collections(transferdb)
    # coll = transferdb["labelled__false_tweets"]
    # curs = coll.find({})
    # for doc in curs:
    #     pprint(doc)
    manually_add_club(transferdb, "Tottenham Hotspur", "Spurs")




def synonym_db():
    transferdb = myclient["transferdb"]
    clubcoll = transferdb["clubs"]
    syncoll = transferdb["club_syns"]
    df = pd.DataFrame(list(clubcoll.find()))

    for index, row in df.iterrows():
        entry = {"club": row["Name"], "syns": generate_syns(row["Name"])}
        syncoll.insert_one(entry)
    manual_clubs

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
    make_player_db(transferdb, path2)
    make_club_db(transferdb, path2)
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


if __name__ == '__main__':
    main()
