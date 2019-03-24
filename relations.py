import csv
import pandas as pd
import pymongo
from pymongo import MongoClient
import numpy as np

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
transferdb = myclient["transferdb"]

def main():
    synthetic_false(["Arsenal", "Manchester United", "Manchester City", "Liverpool", "Chelsea", "Real Madrid", "Barcelona", "Juventus"], ["Thiago Silva"], ["2013", "2014", "2015", "2016", "2017", "2018"])

###### FALSE TWEET FUNCTIONS ######

def synthetic_false(clublist, playerlist, yearlist):
    vars = []
    for i in clublist:
        for j in playerlist:
            for k in yearlist:
                year = k
                list = [j, "", i, year]
                variations = generate_ways(list, "1")
                vars.append(variations)
    make_sythetic_commands(vars)

def make_sythetic_commands(variations):
    file = open("twitter_queries/synfalse_cmds.txt",'w')
    for i in variations:
        vars , year = i
        for j in vars:
            term = '"' + j.strip() + '"'
            start = year+"-06-01"
            end = year+"-08-31"
            cmd = "python ../GetOldTweets/Exporter.py --querysearch " + term + " --maxtweets 100 --since " + start + " --until "+ end +" --output ../info/synres.csv &"
            file.write(cmd+"\n")
    file.close()
    return



def general_query(querys):
    file = open("twitter_queries/query_cmds.txt",'w')
    for i in querys:
        cmd = 'python ../GetOldTweets/Exporter.py --query "' +  i  + '" --since 2017-06-09 --until 2017-08-31 --output ../info/query_terms_2017.csv &'
        file.write(cmd+"\n")
    file.close()
    return

def make_false_commands(tweeters, blacklist):
    file = open("twitter_queries/false_cmds.txt",'w')
    for i in tweeters:
        if i not in blacklist:
            cmd = 'python ../GetOldTweets/Exporter.py --username "' +  i  + '" --since 2018-06-09 --until 2018-08-31 --output ../info/possible2_false.csv &'
        file.write(cmd+"\n")
    file.write("exit1\n")
    file.close()
    return

def find_top_tweeters():
    coll = transferdb["true_transfers"]
    df = pd.DataFrame(list(coll.find()))
    sorted_series = df["username"].value_counts()
    return sorted_series.index[0:12]


###### TRUE TWEET FUNCTIONS ######

def get_true_rels():
    with open('info/relationships.csv', mode='w') as rels:
        rel_writer = csv.writer(rels, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        with open('info/transfers2018.csv') as transfers:
            csv_reader = csv.reader(transfers, delimiter=',')
            for row in csv_reader:
                rel_writer.writerow([row[1], row[2], row[3], row[0]])  # player, from club, to club, date
        with open('info/loans2018.csv') as transfers:
            csv_reader = csv.reader(transfers, delimiter=',')
            for row in csv_reader:
                rel_writer.writerow([row[1], row[2], row[3], row[0]])  # player, from club, to club, date
    return


def make_true_qterms(type):
    true_queries = []
    with open('info/relationships.csv') as transfers:
        csv_reader = csv.reader(transfers, delimiter=',')
        for row in csv_reader:
            true_queries.append(generate_ways(row, type))
    return true_queries


def generate_ways(transfer, type):
    variations = []

    transfer_terms = ["transfer to", "will sign", "having medical", "has signed", "on verge signing", "is signing for", "have been linked"]

    if type=="0":
        for i in transfer_terms:
            query_term = transfer[0] + " " + transfer[1] + " " + transfer[2] + " "  + i
            variations.append(query_term)
    elif type =="1":
        for i in transfer_terms:
            query_term = transfer[0] + " " + transfer[2] + " "  + i
            variations.append(query_term)
    return (variations, transfer[3])

def make_true_commands():
    file = open("twitter_queries/true_cmds.txt",'w')
    player_rels = make_true_qterms("0")
    wait_break=0
    for i in player_rels:
        for j in i[0]:
            term = '"' + j.strip() + '"'
            cmd = "python ../GetOldTweets/Exporter.py --querysearch " + term + " --maxtweets 100 --since 2017-09-01 --until " +date_changer(i[1]) + " --output ../info/true.csv &"
            file.write(cmd+"\n")
            wait_break=wait_break+1
            if wait_break%20==0:
                file.write("wait"+"\n")
    file.close()
    file = open("twitter_queries/true_cmds_shorter.txt",'w')
    player_rels = make_true_qterms("1")
    for i in player_rels:
        for j in i[0]:
            term = '"' + j.strip() + '"'
            cmd = "python ../GetOldTweets/Exporter.py --querysearch " + term + " --maxtweets 100 --since 2017-09-01 --until " +date_changer(i[1]) + " --output ../info/trueShorter.csv &"
            file.write(cmd+"\n")
            wait_break=wait_break+1
            if wait_break%20==0:
                file.write("wait"+"\n")
    file.close()
    return

# reformat date
# set it to the date before the signing was confirmed ** (to be done)
def date_changer(date_str):
    date = date_str.split(" ")
    if len(date)<3:
        return "date"
    else:
        if "[b]" in date[2]:
            date[2]=date[2].replace("[b]",'')
        elif "[a]" in date[2]:
            date[2]=date[2].replace("[a]",'')
        month = str(month_changer(date[1])).strip(" ")

    return date[2] + '-' + month + '-' + date[0]

def month_changer(month_str):
    map = { "January": 01, "February": 02, "March": 03, "April": 04, "May": 05, "June": 06, "July": 07, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12 }
    return map[month_str]

if __name__ == '__main__':
    main()
