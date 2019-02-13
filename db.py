import pymongo
from pymongo import MongoClient
import pandas as pd

def main():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    transferdb = myclient["transferdb"]
    dblist = myclient.list_database_names()
    print (transferdb.collection_names())
    path = "info/true_data_set.csv"
    path2 = "info/transfers2018.csv"
    # store_data(transferdb, path)
    # make_player_db(transferdb, path2)
    query = {"player":"Carl Baker"}
    query_collection(query, "players", transferdb)
    if "mydatabase" in dblist:
        print("The database exists.")


def store_data(transferdb, path):
    mycol = transferdb["true_transfers"]
    df_transfer_true = pd.read_csv(path, sep=';', error_bad_lines=False, encoding="utf-8")
    for i, row in df_transfer_true.iterrows():
        entry = {"username": row['username'], "date": row['date'], "text": row['text']}
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


def query_collection(query, cname, db):
    collection=db[cname]
    docs = collection.find(query)
    for i in docs:
        print(i)
    return


if __name__ == '__main__':
    main()
