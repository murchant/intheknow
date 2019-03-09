import pymongo
from pymongo import MongoClient
import pandas as pd
from pprint import pprint
import urllib2
from bs4 import BeautifulSoup
import csv

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
transferdb = myclient["transferdb"]

def main():
    transferdb = myclient["transferdb"]
    # coll = transferdb["clubs"]
    # entry1 = {"Name": "Tottenham", "syns":"Spurs"}
    # coll.insert_one(entry1)
    # reset_collections(transferdb)
    coll = transferdb["labelled__false_tweets"]
    curs = coll.find({})
    for doc in curs:
            pprint(doc)
    print(coll.count())


def correct_db():


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

def make_club_dbt(entry):
    coll = transferdb["clubs"]
    coll.insert_one(entry)


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

wrongly_labelled = ["5c802abbe8e5df1f0d6e8791", "5c802abce8e5df1f0d6e8792", "5c802b18e8e5df1f0d6e8794", "5c802b25e8e5df1f0d6e8795", "5c802b2be8e5df1f0d6e8796", "5c802b3ce8e5df1f0d6e8797", "5c802b7ae8e5df1f0d6e8799", "5c802b82e8e5df1f0d6e879b", "5c802ba0e8e5df1f0d6e879d", "5c802ba6e8e5df1f0d6e879e", "5c802ba9e8e5df1f0d6e87a0", "5c802c7be8e5df1f0d6e87a2", "5c802c90e8e5df1f0d6e87a4", "5c802c90e8e5df1f0d6e87a4", "5c802cace8e5df1f0d6e87a8", "5c802caee8e5df1f0d6e87a9", "5c802ccfe8e5df1f0d6e87aa", "5c802d4be8e5df1f0d6e87ab", "5c802d77e8e5df1f0d6e87ad", "5c802dcce8e5df1f0d6e87ae", "5c802de2e8e5df1f0d6e87b0", "5c802e9ce8e5df1f0d6e87b5", "5c802f58e8e5df1f0d6e87ba", "5c802f58e8e5df1f0d6e87ba", "5c802fb3e8e5df1f0d6e87be", "5c802fcfe8e5df1f0d6e87bf", "5c802fcfe8e5df1f0d6e87bf", "5c803006e8e5df1f0d6e87c4", "5c8030bbe8e5df1f0d6e87ca", "5c8030f3e8e5df1f0d6e87cb", "5c8031bde8e5df1f0d6e87d1", "5c80321ae8e5df1f0d6e87d3", "5c80321ce8e5df1f0d6e87d4", "5c803220e8e5df1f0d6e87d5", "5c803223e8e5df1f0d6e87d7", "5c803223e8e5df1f0d6e87d7", "5c803225e8e5df1f0d6e87d8", "5c803234e8e5df1f0d6e87db", "5c803238e8e5df1f0d6e87dd", "5c803241e8e5df1f0d6e87df", "5c803242e8e5df1f0d6e87e0", "5c803243e8e5df1f0d6e87e1", "5c80324ee8e5df1f0d6e87e2", "5c8032a8e8e5df1f0d6e87e6", "5c8032a9e8e5df1f0d6e87e7", "5c8032cbe8e5df1f0d6e87e9", "5c8032d5e8e5df1f0d6e87eb", "5c8032d8e8e5df1f0d6e87ec", "5c8032d8e8e5df1f0d6e87ed", "5c8032fae8e5df1f0d6e87ef", "5c803302e8e5df1f0d6e87f0", "5c8033dae8e5df1f0d6e87f4", "5c8033f0e8e5df1f0d6e87f5", "5c8033f8e8e5df1f0d6e87f6", "5c8033f9e8e5df1f0d6e87f7", "5c80343de8e5df1f0d6e87f9", "5c8034f9e8e5df1f0d6e87fd", "5c803519e8e5df1f0d6e8800", "5c803567e8e5df1f0d6e8803", "5c80358be8e5df1f0d6e8805", "5c803593e8e5df1f0d6e8806", "5c803597e8e5df1f0d6e8807", "5c8035ace8e5df1f0d6e8809", "5c803627e8e5df1f0d6e880c", "5c80362ae8e5df1f0d6e880d", "5c80362be8e5df1f0d6e880e", "5c803657e8e5df1f0d6e8812", "5c80366fe8e5df1f0d6e8813", "5c803672e8e5df1f0d6e8814", "5c803686e8e5df1f0d6e8816", "5c803695e8e5df1f0d6e8818", "5c8036d5e8e5df1f0d6e8819", "5c8036d6e8e5df1f0d6e881a", "5c8036eee8e5df1f0d6e881c", "5c8036f5e8e5df1f0d6e881d", "5c803772e8e5df1f0d6e8822", "5c80379ae8e5df1f0d6e8824", "5c80379be8e5df1f0d6e8825", "5c8037eae8e5df1f0d6e8829", "5c80382ee8e5df1f0d6e882a", "5c803892e8e5df1f0d6e882c", "5c8038b0e8e5df1f0d6e882d", "5c8038b6e8e5df1f0d6e882e", "5c8038bce8e5df1f0d6e882f", "5c8038bfe8e5df1f0d6e8830", "5c8038cae8e5df1f0d6e8831", "5c8038e9e8e5df1f0d6e8832", "5c80393ce8e5df1f0d6e8833", "5c803974e8e5df1f0d6e8834", "5c803981e8e5df1f0d6e8835", "5c803a55e8e5df1f0d6e883c", "5c803a74e8e5df1f0d6e883d", "5c803ac1e8e5df1f0d6e8840", "5c803ad0e8e5df1f0d6e8841", "5c803b45e8e5df1f0d6e8846", "5c803b52e8e5df1f0d6e8847", "5c803b61e8e5df1f0d6e8849", "5c803b7fe8e5df1f0d6e884a", "5c803ba7e8e5df1f0d6e884b", "5c803babe8e5df1f0d6e884c", "5c803bbfe8e5df1f0d6e884d", "5c803c59e8e5df1f0d6e884e", "5c803ce2e8e5df1f0d6e8851", "5c803cfae8e5df1f0d6e8854", "5c803d1ce8e5df1f0d6e8856", "5c803d1ee8e5df1f0d6e8857", "5c803d27e8e5df1f0d6e8858", "5c803d30e8e5df1f0d6e8859", "5c803d52e8e5df1f0d6e885c", "5c803df6e8e5df1f0d6e885d", "5c803dfae8e5df1f0d6e885f", "5c803e14e8e5df1f0d6e8861", "5c803e15e8e5df1f0d6e8862", "5c803e29e8e5df1f0d6e8864", "5c803e2be8e5df1f0d6e8865", "5c803e42e8e5df1f0d6e8868", "5c803e92e8e5df1f0d6e886a", "5c803ec1e8e5df1f0d6e886c", "5c803ec3e8e5df1f0d6e886e", "5c803ed8e8e5df1f0d6e886f", "5c803ee6e8e5df1f0d6e8872", "5c803ee8e8e5df1f0d6e8873", "5c803faae8e5df1f0d6e8875", "5c80401ce8e5df1f0d6e8877", "5c80403ce8e5df1f0d6e8879", "5c804066e8e5df1f0d6e887b", "5c80406fe8e5df1f0d6e887c", "5c80409ce8e5df1f0d6e887d", "5c80409de8e5df1f0d6e887e", "5c8040cce8e5df1f0d6e8880", "5c804150e8e5df1f0d6e8883", "5c804195e8e5df1f0d6e8885", "5c8041b6e8e5df1f0d6e8887", "5c8041bee8e5df1f0d6e8888", "5c80421be8e5df1f0d6e8889", "5c804228e8e5df1f0d6e888a", "5c804265e8e5df1f0d6e888c", "5c8042c1e8e5df1f0d6e888f", "5c8042e3e8e5df1f0d6e8892", "5c8042ffe8e5df1f0d6e8895", "5c804310e8e5df1f0d6e8898", "5c804314e8e5df1f0d6e8899", "5c804316e8e5df1f0d6e889a", "5c80431ae8e5df1f0d6e889b", "5c80433ae8e5df1f0d6e889d", "5c804397e8e5df1f0d6e88a0", "5c8043c7e8e5df1f0d6e88a2", "5c8043fee8e5df1f0d6e88a6", "5c804403e8e5df1f0d6e88a7", "5c80442de8e5df1f0d6e88a8", "5c804467e8e5df1f0d6e88a9", "5c8044a3e8e5df1f0d6e88ad", "5c804587e8e5df1f0d6e88af", "5c8045ace8e5df1f0d6e88b0", "5c8045c4e8e5df1f0d6e88b1", "5c804608e8e5df1f0d6e88b3", "5c80460ce8e5df1f0d6e88b5", "5c804639e8e5df1f0d6e88b7", "5c80466ce8e5df1f0d6e88bc", "5c804696e8e5df1f0d6e88bd", "5c8046a0e8e5df1f0d6e88be", "5c8046a4e8e5df1f0d6e88bf", "5c804794e8e5df1f0d6e88c5", "5c8048afe8e5df1f0d6e88c8", "5c8048f1e8e5df1f0d6e88ca", "5c8049cee8e5df1f0d6e88cd", "5c8049ede8e5df1f0d6e88ce", "5c804a02e8e5df1f0d6e88cf", "5c804a46e8e5df1f0d6e88d0", "5c804a48e8e5df1f0d6e88d1", "5c804a4ae8e5df1f0d6e88d2", "5c804a5fe8e5df1f0d6e88d3", "5c804b0ce8e5df1f0d6e88d9", "5c804b58e8e5df1f0d6e88db", "5c804be1e8e5df1f0d6e88e0", "5c804cbde8e5df1f0d6e88e7", "5c804d0fe8e5df1f0d6e88eb", "5c804d57e8e5df1f0d6e88ed", "5c804da9e8e5df1f0d6e88f0", "5c804daee8e5df1f0d6e88f1", "5c804dd8e8e5df1f0d6e88f3", "5c804e1fe8e5df1f0d6e88f4", "5c804e2de8e5df1f0d6e88f6", "5c804ea1e8e5df1f0d6e88fc", "5c804eafe8e5df1f0d6e88fe", "5c804ebfe8e5df1f0d6e88ff", "5c804ec9e8e5df1f0d6e8901", "5c804eeae8e5df1f0d6e8902", "5c804f06e8e5df1f0d6e8904", "5c80510de8e5df1f0d6e890b", "5c805117e8e5df1f0d6e890c", "5c805185e8e5df1f0d6e890e", "5c8051c7e8e5df1f0d6e890f", "5c8051cde8e5df1f0d6e8910", "5c8051f5e8e5df1f0d6e8912", "5c8052b9e8e5df1f0d6e8916", "5c80537fe8e5df1f0d6e891e", "5c8053ade8e5df1f0d6e8920", "5c8053d7e8e5df1f0d6e8921", "5c8054b5e8e5df1f0d6e8924", "5c8054f5e8e5df1f0d6e8926", "5c8055c6e8e5df1f0d6e892d", "5c8055d8e8e5df1f0d6e892e", "5c8055e3e8e5df1f0d6e892f", "5c805607e8e5df1f0d6e8931", "5c8057a7e8e5df1f0d6e8934", "5c8057b8e8e5df1f0d6e8935", "5c8057c9e8e5df1f0d6e8937", "5c805890e8e5df1f0d6e893d", "5c8058ece8e5df1f0d6e893f", "5c80abace8e5df1f0d6e8941", "5c80cbfae8e5df1f0d6e8942", "5c80da87e8e5df1f0d6e8947", "5c80daa1e8e5df1f0d6e8948", "5c80daa3e8e5df1f0d6e8949", "5c80daabe8e5df1f0d6e894a", "5c80e5e6e8e5df1f0d6e8952", "5c80e61de8e5df1f0d6e8953", "5c80f658e8e5df1f0d6e8954", "5c80f659e8e5df1f0d6e8955", "5c80f65fe8e5df1f0d6e8956", "5c80fe47e8e5df1f0d6e895a", "5c810b1ae8e5df1f0d6e895b", "5c81200ae8e5df1f0d6e895c", "5c812010e8e5df1f0d6e895d", "5c8120e9e8e5df1f0d6e895f", "5c81211ce8e5df1f0d6e8960", "5c812187e8e5df1f0d6e8962", "5c812490e8e5df1f0d6e896a", "5c812492e8e5df1f0d6e896b", "5c8124b7e8e5df1f0d6e896c", "5c8124fbe8e5df1f0d6e8971", "5c8124ffe8e5df1f0d6e8972"]

if __name__ == '__main__':
    main()
