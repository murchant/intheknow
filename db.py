import pymongo
from pymongo import MongoClient
import pandas as pd

def main():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    transferdb = myclient["transferdb"]
    print(transferdb.collection_names())
    # DATABASE SETUP
    # path = "info/true_data_set.csv"
    path2 = "info/transfers2018.csv"
    # store_data(transferdb, path)
    # make_player_db(transferdb, path2)
    make_transfer_db(transferdb, path2)
    # query = {"player":"Carl Baker"}
    # query_collection(query, "players", transferdb)


def store_data(transferdb, path):
    mycol = transferdb["true_transfers"]
    df_transfer_true = pd.read_csv(path, sep=';', error_bad_lines=False, encoding="utf-8")
    for i, row in df_transfer_true.iterrows():
        entry = {"username": row['username'].strip(), "date": row['date'].strip(), "text": row['text'].strip()}
        mycol.insert_one(entry)
    return

def make_player_db(transferdb, path):
    coll = transferdb["players"]
    df_transfer_true = pd.read_csv(path, sep=',', error_bad_lines=False, encoding="utf-8")
    for i, row in df_transfer_true.iterrows():
        print(row['Name'])
        print("----------")
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
        entry = {"Date": row["Date"].strip(),"Name": row["Name"].strip(),"Moving from": row["Moving from"].strip(),"Moving to": row["Moving to"].strip()}
        coll.insert_one(entry)
    return

def query_collection(query, cname, db):
    collection=db[cname]
    docs = collection.find(query)
    for i in docs:
        print(i)
    return


if __name__ == '__main__':
    main()
