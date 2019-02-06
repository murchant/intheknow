import csv


def main():
    get_true_rels()
    make_true_qterms()


def get_true_rels():
    with open('relationships.csv', mode='w') as rels:
        rel_writer = csv.writer(rels, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        with open('info/transfers.csv') as transfers:
            csv_reader = csv.reader(transfers, delimiter=',')
            for row in csv_reader:
                rel_writer.writerow([row[1], row[2], row[3], row[0]])  # player, from club, to club, date


def make_true_qterms(type):
    true_queries = []
    with open('relationships.csv') as transfers:
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
    return variations

def make_commands():
    file = open("cmds.txt",'w')
    player_rels = make_true_qterms("0")
    wait_break=0
    for i in player_rels:
        for j in i:
            term = '"' + j + '"'
            cmd = "python GetOldTweets/Exporter.py --querysearch " + term + " --maxtweets 100 --since 2018-06-01 --until 2018-08-30  --output true.csv + &"
            file.write(cmd+"\n")
            wait_break=wait_break+1
            if wait_break%20==0:
                file.write("wait"+"\n")
    file.close()
    file = open("cmdsShorter.txt",'w')
    player_rels = make_true_qterms("1")
    for i in player_rels:
        for j in i:
            term = '"' + j + '"'
            cmd = "python GetOldTweets/Exporter.py --querysearch " + term + " --maxtweets 100 --since 2018-06-01 --until 2018-08-30  --output trueShorter.csv + &"
            file.write(cmd+"\n")
            wait_break=wait_break+1
            if wait_break%20==0:
                file.write("wait"+"\n")
    file.close()
    return

if __name__ == '__main__':
    main()
