import csv
import pandas as pd

def main():
    get_true_rels()
    # make_true_qterms()


def get_true_rels():
    with open('info/relationships.csv', mode='w') as rels:
        rel_writer = csv.writer(rels, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        with open('info/transfers2018.csv') as transfers:
            csv_reader = csv.reader(transfers, delimiter=',')
            for row in csv_reader:
                rel_writer.writerow([row[1], row[2], row[3], row[0]])  # player, from club, to club, date


def make_true_qterms(type):
    true_queries = []
    with open('info/relationships.csv') as transfers:
        csv_reader = csv.reader(transfers, delimiter=',')
        for row in csv_reader:
            true_queries.append(generate_ways(row, type))
    return true_queries


def generate_ways(transfer, type):
    variations = []

    transfer_terms = ["transfer", "signing", "deal", "medical", "close", "talks", "signed", "verge", "opened"]

    if type=="0":
        for i in transfer_terms:
            query_term = transfer[0] + " " + transfer[1] + " " + transfer[2] + " "  + i
            variations.append(query_term)
    elif type =="1":
        for i in transfer_terms:
            query_term = transfer[0] + " " + transfer[2] + " "  + i
            variations.append(query_term)
    return (variations, transfer[3])

def make_commands():
    file = open("twitter_queries/cmds.txt",'w')
    player_rels = make_true_qterms("0")
    wait_break=0
    for i in player_rels:
        for j in i[0]:
            term = '"' + j + '"'
            cmd = "python ../GetOldTweets/Exporter.py --querysearch " + term + " --maxtweets 100 --since 2017-09-01 --until " +date_changer(i[1]) + " --output ../info/true.csv &"
            file.write(cmd+"\n")
            wait_break=wait_break+1
            if wait_break%20==0:
                file.write("wait"+"\n")
    file.close()
    file = open("twitter_queries/cmdsShorter.txt",'w')
    player_rels = make_true_qterms("1")
    for i in player_rels:
        for j in i[0]:
            term = '"' + j + '"'
            cmd = "python ../GetOldTweets/Exporter.py --querysearch " + term + " --maxtweets 100 --since 2017-09-01 --until " +date_changer(i[1]) + " --output ../info/trueShorter.csv &"
            file.write(cmd+"\n")
            wait_break=wait_break+1
            if wait_break%20==0:
                file.write("wait"+"\n")
    file.close()
    return

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
