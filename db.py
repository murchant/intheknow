import pymongo
from pymongo import MongoClient
import pandas as pd

def main():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    transferdb = myclient["transferdb"]
    relsdb = myclient["truetransfers"]
    dblist = myclient.list_database_names()
    # path = "info/transfers2018.csv"
    # store_true(transferdb, path)
    query = {"username":"SoccerTube2"}
    query_collection(query, "true_transfers")

    if "mydatabase" in dblist:
        print("The database exists.")


def store_true(transferdb, path):
    mycol = transferdb["true_transfers"]
    df_transfer_true = pd.read_csv(path, sep=';', error_bad_lines=False, encoding="utf-8-sig")
    for i, row in df_transfer_true.iterrows():
        entry = {"username": row['username'], "date": row['date'], "text": row['text']}
        mycol.insert_one(entry)
    return


def query_collection(query, cname):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["transferdb"]
    collection=db[cname]
    docs = collection.find(query)
    for i in docs:
        print(i)
    return



if __name__ == '__main__':
    main()
