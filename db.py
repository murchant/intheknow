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


    # store_syn_false("info/synres.csv")
    true = transferdb["true_transfers"]
    false = transferdb["synfalse_transfers"]
    print(false.count())


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
    mycol = transferdb["true_transfers"]
    df_transfer_true = pd.read_csv(path, sep=',', error_bad_lines=False, encoding="utf-8")
    for i, row in df_transfer_true.iterrows():
        entry = {"username": row['username'].strip(), "date": row['date'].strip(), "tweet_text": row['text'].strip(), "label":"True"}
        mycol.insert_one(entry)
    return

def store_syn_false(path):
    coll = transferdb["synfalse_transfers"]
    df_transfer_synfalse = pd.read_csv(path, sep=';', error_bad_lines=False, encoding="utf-8")
    for i, row in df_transfer_synfalse.iterrows():
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


def intersect_db():
    coll = transferdb["labelled__false_tweets"]
    curs = coll.find({})
    collnew = transferdb["labelled__false_querys"]
    for doc in curs:
            query = {'tweet_text': doc['tweet_text']}
            collnew.delete_one(query)


wrongly_labelled1 = ["5c802abbe8e5df1f0d6e8791", "5c802abce8e5df1f0d6e8792", "5c802b18e8e5df1f0d6e8794", "5c802b25e8e5df1f0d6e8795", "5c802b2be8e5df1f0d6e8796", "5c802b3ce8e5df1f0d6e8797", "5c802b7ae8e5df1f0d6e8799", "5c802b82e8e5df1f0d6e879b", "5c802ba0e8e5df1f0d6e879d", "5c802ba6e8e5df1f0d6e879e", "5c802ba9e8e5df1f0d6e87a0", "5c802c7be8e5df1f0d6e87a2", "5c802c90e8e5df1f0d6e87a4", "5c802c90e8e5df1f0d6e87a4", "5c802cace8e5df1f0d6e87a8", "5c802caee8e5df1f0d6e87a9", "5c802ccfe8e5df1f0d6e87aa", "5c802d4be8e5df1f0d6e87ab", "5c802d77e8e5df1f0d6e87ad", "5c802dcce8e5df1f0d6e87ae", "5c802de2e8e5df1f0d6e87b0", "5c802e9ce8e5df1f0d6e87b5", "5c802f58e8e5df1f0d6e87ba", "5c802f58e8e5df1f0d6e87ba", "5c802fb3e8e5df1f0d6e87be", "5c802fcfe8e5df1f0d6e87bf", "5c802fcfe8e5df1f0d6e87bf", "5c803006e8e5df1f0d6e87c4", "5c8030bbe8e5df1f0d6e87ca", "5c8030f3e8e5df1f0d6e87cb", "5c8031bde8e5df1f0d6e87d1", "5c80321ae8e5df1f0d6e87d3", "5c80321ce8e5df1f0d6e87d4", "5c803220e8e5df1f0d6e87d5", "5c803223e8e5df1f0d6e87d7", "5c803223e8e5df1f0d6e87d7", "5c803225e8e5df1f0d6e87d8", "5c803234e8e5df1f0d6e87db", "5c803238e8e5df1f0d6e87dd", "5c803241e8e5df1f0d6e87df", "5c803242e8e5df1f0d6e87e0", "5c803243e8e5df1f0d6e87e1", "5c80324ee8e5df1f0d6e87e2", "5c8032a8e8e5df1f0d6e87e6", "5c8032a9e8e5df1f0d6e87e7", "5c8032cbe8e5df1f0d6e87e9", "5c8032d5e8e5df1f0d6e87eb", "5c8032d8e8e5df1f0d6e87ec", "5c8032d8e8e5df1f0d6e87ed", "5c8032fae8e5df1f0d6e87ef", "5c803302e8e5df1f0d6e87f0", "5c8033dae8e5df1f0d6e87f4", "5c8033f0e8e5df1f0d6e87f5", "5c8033f8e8e5df1f0d6e87f6", "5c8033f9e8e5df1f0d6e87f7", "5c80343de8e5df1f0d6e87f9", "5c8034f9e8e5df1f0d6e87fd", "5c803519e8e5df1f0d6e8800", "5c803567e8e5df1f0d6e8803", "5c80358be8e5df1f0d6e8805", "5c803593e8e5df1f0d6e8806", "5c803597e8e5df1f0d6e8807", "5c8035ace8e5df1f0d6e8809", "5c803627e8e5df1f0d6e880c", "5c80362ae8e5df1f0d6e880d", "5c80362be8e5df1f0d6e880e", "5c803657e8e5df1f0d6e8812", "5c80366fe8e5df1f0d6e8813", "5c803672e8e5df1f0d6e8814", "5c803686e8e5df1f0d6e8816", "5c803695e8e5df1f0d6e8818", "5c8036d5e8e5df1f0d6e8819", "5c8036d6e8e5df1f0d6e881a", "5c8036eee8e5df1f0d6e881c", "5c8036f5e8e5df1f0d6e881d", "5c803772e8e5df1f0d6e8822", "5c80379ae8e5df1f0d6e8824", "5c80379be8e5df1f0d6e8825", "5c8037eae8e5df1f0d6e8829", "5c80382ee8e5df1f0d6e882a", "5c803892e8e5df1f0d6e882c", "5c8038b0e8e5df1f0d6e882d", "5c8038b6e8e5df1f0d6e882e", "5c8038bce8e5df1f0d6e882f", "5c8038bfe8e5df1f0d6e8830", "5c8038cae8e5df1f0d6e8831", "5c8038e9e8e5df1f0d6e8832", "5c80393ce8e5df1f0d6e8833", "5c803974e8e5df1f0d6e8834", "5c803981e8e5df1f0d6e8835", "5c803a55e8e5df1f0d6e883c", "5c803a74e8e5df1f0d6e883d", "5c803ac1e8e5df1f0d6e8840", "5c803ad0e8e5df1f0d6e8841", "5c803b45e8e5df1f0d6e8846", "5c803b52e8e5df1f0d6e8847", "5c803b61e8e5df1f0d6e8849", "5c803b7fe8e5df1f0d6e884a", "5c803ba7e8e5df1f0d6e884b", "5c803babe8e5df1f0d6e884c", "5c803bbfe8e5df1f0d6e884d", "5c803c59e8e5df1f0d6e884e", "5c803ce2e8e5df1f0d6e8851", "5c803cfae8e5df1f0d6e8854", "5c803d1ce8e5df1f0d6e8856", "5c803d1ee8e5df1f0d6e8857", "5c803d27e8e5df1f0d6e8858", "5c803d30e8e5df1f0d6e8859", "5c803d52e8e5df1f0d6e885c", "5c803df6e8e5df1f0d6e885d", "5c803dfae8e5df1f0d6e885f", "5c803e14e8e5df1f0d6e8861", "5c803e15e8e5df1f0d6e8862", "5c803e29e8e5df1f0d6e8864", "5c803e2be8e5df1f0d6e8865", "5c803e42e8e5df1f0d6e8868", "5c803e92e8e5df1f0d6e886a", "5c803ec1e8e5df1f0d6e886c", "5c803ec3e8e5df1f0d6e886e", "5c803ed8e8e5df1f0d6e886f", "5c803ee6e8e5df1f0d6e8872", "5c803ee8e8e5df1f0d6e8873", "5c803faae8e5df1f0d6e8875", "5c80401ce8e5df1f0d6e8877", "5c80403ce8e5df1f0d6e8879", "5c804066e8e5df1f0d6e887b", "5c80406fe8e5df1f0d6e887c", "5c80409ce8e5df1f0d6e887d", "5c80409de8e5df1f0d6e887e", "5c8040cce8e5df1f0d6e8880", "5c804150e8e5df1f0d6e8883", "5c804195e8e5df1f0d6e8885", "5c8041b6e8e5df1f0d6e8887", "5c8041bee8e5df1f0d6e8888", "5c80421be8e5df1f0d6e8889", "5c804228e8e5df1f0d6e888a", "5c804265e8e5df1f0d6e888c", "5c8042c1e8e5df1f0d6e888f", "5c8042e3e8e5df1f0d6e8892", "5c8042ffe8e5df1f0d6e8895", "5c804310e8e5df1f0d6e8898", "5c804314e8e5df1f0d6e8899", "5c804316e8e5df1f0d6e889a", "5c80431ae8e5df1f0d6e889b", "5c80433ae8e5df1f0d6e889d", "5c804397e8e5df1f0d6e88a0", "5c8043c7e8e5df1f0d6e88a2", "5c8043fee8e5df1f0d6e88a6", "5c804403e8e5df1f0d6e88a7", "5c80442de8e5df1f0d6e88a8", "5c804467e8e5df1f0d6e88a9", "5c8044a3e8e5df1f0d6e88ad", "5c804587e8e5df1f0d6e88af", "5c8045ace8e5df1f0d6e88b0", "5c8045c4e8e5df1f0d6e88b1", "5c804608e8e5df1f0d6e88b3", "5c80460ce8e5df1f0d6e88b5", "5c804639e8e5df1f0d6e88b7", "5c80466ce8e5df1f0d6e88bc", "5c804696e8e5df1f0d6e88bd", "5c8046a0e8e5df1f0d6e88be", "5c8046a4e8e5df1f0d6e88bf", "5c804794e8e5df1f0d6e88c5", "5c8048afe8e5df1f0d6e88c8", "5c8048f1e8e5df1f0d6e88ca", "5c8049cee8e5df1f0d6e88cd", "5c8049ede8e5df1f0d6e88ce", "5c804a02e8e5df1f0d6e88cf", "5c804a46e8e5df1f0d6e88d0", "5c804a48e8e5df1f0d6e88d1", "5c804a4ae8e5df1f0d6e88d2", "5c804a5fe8e5df1f0d6e88d3", "5c804b0ce8e5df1f0d6e88d9", "5c804b58e8e5df1f0d6e88db", "5c804be1e8e5df1f0d6e88e0", "5c804cbde8e5df1f0d6e88e7", "5c804d0fe8e5df1f0d6e88eb", "5c804d57e8e5df1f0d6e88ed", "5c804da9e8e5df1f0d6e88f0", "5c804daee8e5df1f0d6e88f1", "5c804dd8e8e5df1f0d6e88f3", "5c804e1fe8e5df1f0d6e88f4", "5c804e2de8e5df1f0d6e88f6", "5c804ea1e8e5df1f0d6e88fc", "5c804eafe8e5df1f0d6e88fe", "5c804ebfe8e5df1f0d6e88ff", "5c804ec9e8e5df1f0d6e8901", "5c804eeae8e5df1f0d6e8902", "5c804f06e8e5df1f0d6e8904", "5c80510de8e5df1f0d6e890b", "5c805117e8e5df1f0d6e890c", "5c805185e8e5df1f0d6e890e", "5c8051c7e8e5df1f0d6e890f", "5c8051cde8e5df1f0d6e8910", "5c8051f5e8e5df1f0d6e8912", "5c8052b9e8e5df1f0d6e8916", "5c80537fe8e5df1f0d6e891e", "5c8053ade8e5df1f0d6e8920", "5c8053d7e8e5df1f0d6e8921", "5c8054b5e8e5df1f0d6e8924", "5c8054f5e8e5df1f0d6e8926", "5c8055c6e8e5df1f0d6e892d", "5c8055d8e8e5df1f0d6e892e", "5c8055e3e8e5df1f0d6e892f", "5c805607e8e5df1f0d6e8931", "5c8057a7e8e5df1f0d6e8934", "5c8057b8e8e5df1f0d6e8935", "5c8057c9e8e5df1f0d6e8937", "5c805890e8e5df1f0d6e893d", "5c8058ece8e5df1f0d6e893f", "5c80abace8e5df1f0d6e8941", "5c80cbfae8e5df1f0d6e8942", "5c80da87e8e5df1f0d6e8947", "5c80daa1e8e5df1f0d6e8948", "5c80daa3e8e5df1f0d6e8949", "5c80daabe8e5df1f0d6e894a", "5c80e5e6e8e5df1f0d6e8952", "5c80e61de8e5df1f0d6e8953", "5c80f658e8e5df1f0d6e8954", "5c80f659e8e5df1f0d6e8955", "5c80f65fe8e5df1f0d6e8956", "5c80fe47e8e5df1f0d6e895a", "5c810b1ae8e5df1f0d6e895b", "5c81200ae8e5df1f0d6e895c", "5c812010e8e5df1f0d6e895d", "5c8120e9e8e5df1f0d6e895f", "5c81211ce8e5df1f0d6e8960", "5c812187e8e5df1f0d6e8962", "5c812490e8e5df1f0d6e896a", "5c812492e8e5df1f0d6e896b", "5c8124b7e8e5df1f0d6e896c", "5c8124fbe8e5df1f0d6e8971", "5c8124ffe8e5df1f0d6e8972", "5c802b4fe8e5df1f0d6e8798", "5c802cace8e5df1f0d6e87a7", "5c802f5fe8e5df1f0d6e87bb", "5c802ffbe8e5df1f0d6e87c2", "5c803507e8e5df1f0d6e87fe", "5c803625e8e5df1f0d6e880b"]

wrongly_labelled2 = ["5c86d3d7e8e5df563b91eadc",
"5c86d3d8e8e5df563b91eadd", "5c86d3d9e8e5df563b91eade",
"5c86d3dbe8e5df563b91eadf", "5c86d3dce8e5df563b91eae0",
"5c86d3dee8e5df563b91eae1", "5c86d417e8e5df563b91eae2",
"5c86d420e8e5df563b91eae5", "5c86d41ae8e5df563b91eae3",
"5c86d41fe8e5df563b91eae4", "5c86ed3fe8e5df563b91eb50",
"5c86d429e8e5df563b91eae6", "5c86d42be8e5df563b91eae7",
"5c86d42de8e5df563b91eae8", "5c86d52fe8e5df563b91eae9",
"5c86d539e8e5df563b91eaea", "5c86d53ae8e5df563b91eaeb",
"5c86d672e8e5df563b91eafc","5c86d682e8e5df563b91eb00",
"5c86d68be8e5df563b91eb01","5c86d6a6e8e5df563b91eb02",
"5c86d6abe8e5df563b91eb03","5c86d6ace8e5df563b91eb04",
"5c86d6ade8e5df563b91eb05","5c86d6bce8e5df563b91eb06",
"5c86d72fe8e5df563b91eb08","5c86d754e8e5df563b91eb09",
"5c86d75be8e5df563b91eb0a","5c86d75ce8e5df563b91eb0b",
"5c86d75ce8e5df563b91eb0c","5c86d762e8e5df563b91eb0d",
"5c86d763e8e5df563b91eb0e","5c86d672e8e5df563b91eafc",
"5c86d682e8e5df563b91eb00","5c86d68be8e5df563b91eb01",
"5c86d6a6e8e5df563b91eb02","5c86d6abe8e5df563b91eb03",
"5c86d6ace8e5df563b91eb04","5c86d6ade8e5df563b91eb05",
"5c86d6bce8e5df563b91eb06","5c86d72fe8e5df563b91eb08",
"5c86d754e8e5df563b91eb09","5c86d75be8e5df563b91eb0a",
"5c86d75ce8e5df563b91eb0b","5c86d75ce8e5df563b91eb0c",
"5c86d762e8e5df563b91eb0d","5c86d763e8e5df563b91eb0e",
"5c86d854e8e5df563b91eb28", "5c86d85ee8e5df563b91eb2b",
"5c86d8fee8e5df563b91eb2d", "5c86d8ffe8e5df563b91eb2e",
"5c86d905e8e5df563b91eb30", "5c86d925e8e5df563b91eb34",
"5c86d926e8e5df563b91eb35", "5c86d93ae8e5df563b91eb36",
"5c86d94de8e5df563b91eb38", "5c86d94ee8e5df563b91eb39",
"5c86d94fe8e5df563b91eb3a", "5c86d950e8e5df563b91eb3b",
"5c86d951e8e5df563b91eb3c", "5c86d951e8e5df563b91eb3d",
"5c86d954e8e5df563b91eb3e", "5c86d95ce8e5df563b91eb3f",
"5c86d95de8e5df563b91eb40", "5c86d968e8e5df563b91eb41",
"5c86d96de8e5df563b91eb42", "5c86d96ee8e5df563b91eb43",
"5c86d974e8e5df563b91eb44", "5c86d975e8e5df563b91eb45",
"5c86d982e8e5df563b91eb46", "5c86d984e8e5df563b91eb47",
"5c86d985e8e5df563b91eb48", "5c86d987e8e5df563b91eb49",
"5c86d988e8e5df563b91eb4a", "5c86d989e8e5df563b91eb4b",
"5c86d98de8e5df563b91eb4c", "5c86d991e8e5df563b91eb4d",
"5c86da02e8e5df563b91eb4e", "5c86ed21e8e5df563b91eb4f",
"5c86ed3fe8e5df563b91eb50", "5c86ed56e8e5df563b91eb51",
"5c86ed65e8e5df563b91eb53", "5c86ed6be8e5df563b91eb56",
"5c86ed6ce8e5df563b91eb57", "5c86eda3e8e5df563b91eb58",
"5c86eda4e8e5df563b91eb59", "5c86eda6e8e5df563b91eb5a",
"5c86edbbe8e5df563b91eb5b", "5c86edbce8e5df563b91eb5c",
"5c86edbde8e5df563b91eb5d", "5c86edbee8e5df563b91eb5e",
"5c86edc3e8e5df563b91eb60", "5c86edc6e8e5df563b91eb61",
"5c86edc9e8e5df563b91eb62", "5c86edcbe8e5df563b91eb63",
"5c86edd9e8e5df563b91eb64", "5c86ede5e8e5df563b91eb65",
"5c86edede8e5df563b91eb66", "5c86edeee8e5df563b91eb67",
"5c86eefae8e5df563b91eb6c", "5c86ef13e8e5df563b91eb6e",
"5c86ef14e8e5df563b91eb6f", "5c86ef21e8e5df563b91eb70",
"5c86ef8fe8e5df563b91eb71", "5c86ef92e8e5df563b91eb72",
"5c86ef92e8e5df563b91eb73", "5c86ef93e8e5df563b91eb74",
"5c86efbbe8e5df563b91eb75", "5c86f090e8e5df563b91eb76",
"5c86f092e8e5df563b91eb77", "5c86f094e8e5df563b91eb78",
"5c86f096e8e5df563b91eb79", "5c86f120e8e5df563b91eb7b",
"5c86f13ae8e5df563b91eb7c", "5c86f2b9e8e5df563b91eb99",
"5c86f13de8e5df563b91eb7d", "5c86f13ee8e5df563b91eb7e",
"5c86f13fe8e5df563b91eb7f", "5c86f146e8e5df563b91eb80",
"5c86f149e8e5df563b91eb81", "5c86f156e8e5df563b91eb82",
"5c86f166e8e5df563b91eb83", "5c86f280e8e5df563b91eb86",
"5c86f290e8e5df563b91eb95", "5c86f29fe8e5df563b91eb96",
"5c86f2a6e8e5df563b91eb97","5c86f2c4e8e5df563b91eb9a",
"5c86f2c4e8e5df563b91eb9b","5c86f2c5e8e5df563b91eb9c",
"5c86f2c6e8e5df563b91eb9d","5c86f2c7e8e5df563b91eb9e",
"5c86f2c8e8e5df563b91eb9f","5c86f2c9e8e5df563b91eba0",
"5c86f2c9e8e5df563b91eba1","5c86f2cae8e5df563b91eba2",
"5c86f2cce8e5df563b91eba3","5c86f2cde8e5df563b91eba4",
"5c86f2cee8e5df563b91eba5","5c86f2cfe8e5df563b91eba6",
"5c86f2cfe8e5df563b91eba7","5c86f2d2e8e5df563b91eba8",
"5c86f2d2e8e5df563b91eba9","5c86f2d3e8e5df563b91ebaa",
"5c86f2d4e8e5df563b91ebab","5c86f2d5e8e5df563b91ebac",
"5c86f2d5e8e5df563b91ebad","5c86f2e2e8e5df563b91ebae",
"5c86f300e8e5df563b91ebaf","5c86f36ce8e5df563b91ebb0",
"5c86f46ce8e5df563b91ebb4","5c86f473e8e5df563b91ebb5",
"5c86f476e8e5df563b91ebb6","5c86f479e8e5df563b91ebb7",
"5c86f47ae8e5df563b91ebb8","5c86f47be8e5df563b91ebb9",
"5c86f47ee8e5df563b91ebba","5c86f482e8e5df563b91ebbb",
"5c86f487e8e5df563b91ebbc","5c86f488e8e5df563b91ebbd",
"5c86f48ce8e5df563b91ebbe","5c86f48de8e5df563b91ebbf",
"5c86f60ae8e5df563b91ebc0","5c86f624e8e5df563b91ebc1",
"5c86f746e8e5df563b91ebc2","5c86f747e8e5df563b91ebc3",
"5c86f758e8e5df563b91ebc4","5c86f76de8e5df563b91ebc5",
"5c86f76ee8e5df563b91ebc6","5c86f76fe8e5df563b91ebc7",
"5c86f770e8e5df563b91ebc8","5c86f771e8e5df563b91ebc9",
"5c86f772e8e5df563b91ebca","5c86f775e8e5df563b91ebcb",
"5c86f777e8e5df563b91ebcc","5c86f777e8e5df563b91ebcd",
"5c86f778e8e5df563b91ebce","5c86f88ce8e5df563b91ebcf",
"5c86f8b8e8e5df563b91ebd0","5c86f8bae8e5df563b91ebd1",
"5c86f8bce8e5df563b91ebd2","5c86f8bee8e5df563b91ebd3",
"5c86f8c9e8e5df563b91ebd4","5c86f8cbe8e5df563b91ebd5",
"5c86f8cde8e5df563b91ebd6","5c86f8cde8e5df563b91ebd7",
"5c86f8cee8e5df563b91ebd8","5c86f8cfe8e5df563b91ebd9",
"5c86f8d0e8e5df563b91ebda","5c86f8d4e8e5df563b91ebdb",
"5c86f8d6e8e5df563b91ebdc","5c86f9c3e8e5df563b91ebde",
"5c86f9c4e8e5df563b91ebdf","5c86f9c5e8e5df563b91ebe0",
"5c86f9c6e8e5df563b91ebe1","5c86f9c6e8e5df563b91ebe2",
"5c86f9cbe8e5df563b91ebe3","5c86f9cce8e5df563b91ebe4",
"5c86f9cde8e5df563b91ebe5","5c86f9cde8e5df563b91ebe6",
"5c86f9cee8e5df563b91ebe7","5c86f9cfe8e5df563b91ebe8",
"5c86f9e5e8e5df563b91ebe9","5c86f9e8e8e5df563b91ebea",
"5c86f9f1e8e5df563b91ebeb","5c86f9f2e8e5df563b91ebec",
"5c86f9f3e8e5df563b91ebed","5c86f9fde8e5df563b91ebee",
"5c86facde8e5df563b91ebef","5c86fafee8e5df563b91ebf0",
"5c86fbfce8e5df563b91ebf2","5c86fbfce8e5df563b91ebf2",
"5c86fc10e8e5df563b91ebf3","5c86fcdae8e5df563b91ebf5",
"5c86fcdbe8e5df563b91ebf6","5c86fcdee8e5df563b91ebf7",
"5c86fdf1e8e5df563b91ebf8","5c86fee8e8e5df563b91ebf9",
"5c86ff54e8e5df563b91ebfa","5c86ffdfe8e5df563b91ebfb",
"5c86ffe1e8e5df563b91ebfc","5c870008e8e5df563b91ebfd",
"5c87000ee8e5df563b91ebfe","5c87000fe8e5df563b91ebff",
"5c870012e8e5df563b91ec00","5c870012e8e5df563b91ec01",
"5c870013e8e5df563b91ec02","5c870014e8e5df563b91ec03",
"5c870015e8e5df563b91ec04","5c8705f6e8e5df563b91ec26",
"5c870016e8e5df563b91ec06","5c870150e8e5df563b91ec08",
"5c870157e8e5df563b91ec09","5c870177e8e5df563b91ec0a",
"5c8701b6e8e5df563b91ec0b","5c8701c4e8e5df563b91ec0c",
"5c870242e8e5df563b91ec0d","5c870253e8e5df563b91ec0e",
"5c87025ae8e5df563b91ec0f","5c87025fe8e5df563b91ec10",
"5c870261e8e5df563b91ec11","5c870263e8e5df563b91ec12",
"5c87026ce8e5df563b91ec13","5c87032ee8e5df563b91ec14",
"5c870330e8e5df563b91ec15","5c870335e8e5df563b91ec16",
"5c870336e8e5df563b91ec17","5c8703fde8e5df563b91ec18",
"5c870412e8e5df563b91ec19","5c870413e8e5df563b91ec1a",
"5c8704d9e8e5df563b91ec1b","5c8704f0e8e5df563b91ec1c",
"5c8704fbe8e5df563b91ec1d","5c8704fce8e5df563b91ec1e",
"5c8704ffe8e5df563b91ec1f","5c87050be8e5df563b91ec20",
"5c87050de8e5df563b91ec21","5c870518e8e5df563b91ec22",
"5c8705b5e8e5df563b91ec23","5c8705c8e8e5df563b91ec24",
"5c8705e7e8e5df563b91ec25","5c8705f6e8e5df563b91ec26",
"5c86fbfce8e5df563b91ebf2","5c86fc10e8e5df563b91ebf3",
"5c86fcdae8e5df563b91ebf5","5c86fcdbe8e5df563b91ebf6",
"5c86fcdee8e5df563b91ebf7","5c86fdf1e8e5df563b91ebf8",
"5c86fee8e8e5df563b91ebf9","5c86ff54e8e5df563b91ebfa",
"5c86ffdfe8e5df563b91ebfb","5c86ffe1e8e5df563b91ebfc",
"5c870008e8e5df563b91ebfd","5c87000ee8e5df563b91ebfe",
"5c87000fe8e5df563b91ebff","5c870012e8e5df563b91ec00",
"5c870012e8e5df563b91ec01","5c870013e8e5df563b91ec02",
"5c870014e8e5df563b91ec03","5c870015e8e5df563b91ec04",
"5c870015e8e5df563b91ec05","5c870016e8e5df563b91ec06",
"5c870150e8e5df563b91ec08","5c870157e8e5df563b91ec09",
"5c870177e8e5df563b91ec0a","5c8701b6e8e5df563b91ec0b",
"5c8701c4e8e5df563b91ec0c","5c870242e8e5df563b91ec0d",
"5c870253e8e5df563b91ec0e","5c87025ae8e5df563b91ec0f",
"5c87025fe8e5df563b91ec10","5c870261e8e5df563b91ec11",
"5c870263e8e5df563b91ec12","5c87026ce8e5df563b91ec13",
"5c87032ee8e5df563b91ec14","5c870330e8e5df563b91ec15",
"5c870335e8e5df563b91ec16","5c870336e8e5df563b91ec17",
"5c8703fde8e5df563b91ec18","5c870412e8e5df563b91ec19",
"5c870413e8e5df563b91ec1a","5c8704d9e8e5df563b91ec1b",
"5c8704f0e8e5df563b91ec1c","5c8704fbe8e5df563b91ec1d",
"5c8704fce8e5df563b91ec1e","5c8704ffe8e5df563b91ec1f",
"5c87050be8e5df563b91ec20","5c87050de8e5df563b91ec21",
"5c870518e8e5df563b91ec22","5c8705b5e8e5df563b91ec23",
"5c8705c8e8e5df563b91ec24","5c8705e7e8e5df563b91ec25",
"5c8705f6e8e5df563b91ec26","5c87061ce8e5df563b91ec28",
"5c87069ce8e5df563b91ec29","5c8706a0e8e5df563b91ec2a",
"5c8706b8e8e5df563b91ec2b","5c8706d5e8e5df563b91ec2c",
"5c870781e8e5df563b91ec2d","5c870786e8e5df563b91ec2e",
"5c87079ae8e5df563b91ec2f","5c8707b6e8e5df563b91ec30",
"5c87084de8e5df563b91ec31","5c870857e8e5df563b91ec32",
"5c87086ae8e5df563b91ec33","5c8773c2e8e5df5b9abcbc87",
"5c877909e8e5df5b9abcbc88","5c87790de8e5df5b9abcbc89",
"5c877be8e8e5df5b9abcbc8b","5c878628e8e5df5b9abcbc8c",
"5c878704e8e5df5b9abcbc8d","5c87893be8e5df5b9abcbc8e",
"5c8789dde8e5df5b9abcbc90","5c878a19e8e5df5b9abcbc91",
"5c878d24e8e5df5b9abcbc92","5c878d9be8e5df5b9abcbc93",
"5c87921fe8e5df5b9abcbc95","5c87996de8e5df5b9abcbca0",
"5c879977e8e5df5b9abcbca1","5c8799bbe8e5df5b9abcbca2",
"5c879df6e8e5df5b9abcbca6","5c879e05e8e5df5b9abcbca7",
"5c879f04e8e5df5b9abcbca8","5c87a798e8e5df5b9abcbcaf",
"5c87a7d4e8e5df5b9abcbcb1","5c87a952e8e5df5b9abcbcb2",
"5c87aa6be8e5df5b9abcbcb3","5c87ab81e8e5df5b9abcbcb4",
"5c87ac35e8e5df5b9abcbcb5","5c87b3b1e8e5df5b9abcbcb6",
"5c87b6f9e8e5df5b9abcbcb7","5c87b9cbe8e5df5b9abcbcb8",
"5c87ba28e8e5df5b9abcbcb9","5c87bbc9e8e5df5b9abcbcba",
"5c87bfc0e8e5df5b9abcbcbd","5c87996de8e5df5b9abcbca0",
"5c879977e8e5df5b9abcbca1","5c8799bbe8e5df5b9abcbca2",
"5c879df6e8e5df5b9abcbca6","5c879e05e8e5df5b9abcbca7",
"5c879f04e8e5df5b9abcbca8","5c87a798e8e5df5b9abcbcaf",
"5c87a7d4e8e5df5b9abcbcb1","5c87a952e8e5df5b9abcbcb2",
"5c87aa6be8e5df5b9abcbcb3","5c87ab81e8e5df5b9abcbcb4",
"5c87ac35e8e5df5b9abcbcb5","5c87b3b1e8e5df5b9abcbcb6",
"5c87b6f9e8e5df5b9abcbcb7","5c87b9cbe8e5df5b9abcbcb8",
"5c87ba28e8e5df5b9abcbcb9","5c87bbc9e8e5df5b9abcbcba",
"5c87bfc0e8e5df5b9abcbcbd", "5c87c873e8e5df5b9abcbcc5",
"5c87c8d2e8e5df5b9abcbcc6", "5c87cc34e8e5df5b9abcbcc7", "5c87c3b1e8e5df5b9abcbcc4"]

if __name__ == '__main__':
    main()
