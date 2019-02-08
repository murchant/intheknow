import pymongo
from pymongo import MongoClient

def main():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["mydatabase"]
    dblist = myclient.list_database_names()
    mycol = mydb["customers"]
    print(dblist)
    print(mydb.list_collection_names())
    mydict = { "name": "John", "address": "Highway 37" }
    x = mycol.insert_one(mydict)
    print(x.inserted_id)


    if "mydatabase" in dblist:
        print("The database exists.")

if __name__ == '__main__':
    main()
