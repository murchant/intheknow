import pymongo
from pymongo import MongoClient
import pandas as pd
from pprint import pprint

def main():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    transferdb = myclient["transferdb"]
    # DATABASE SETUP
    # path = "info/true_data_set.csv"
    # path2 = "info/transfers2018.csv"
    # store_data(transferdb, path)
    # make_player_db(transferdb, path2)
    # make_transfer_db(transferdb, path2)
    # reset_collections(transferdb)
    coll_list=transferdb.list_collection_names()
    print(coll_list)


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
        entry1 = {"Moving from": row['Name'].strip()}
        entry2 = {"Moving to": row['Name'].strip()}
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
