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


def make_true_qterms():
    true_queries = []
    with open('relationships.csv') as transfers:
        csv_reader = csv.reader(transfers, delimiter=',')
        for row in csv_reader:
            true_queries.append(generate_ways(row))
    print(true_queries)


def generate_ways(transfer):
    variations = []
    transfer_terms = ["transfer", "signing", "done deal", "in the know", "medical", "close", "talks with", "talks", "signed", "verge"]

    for i in transfer_terms:
        query_term = transfer[0] + " " + transfer[1] + " " + transfer[2] + " " + i
        variations.append(query_term)
    return variations


if __name__ == '__main__':
    main()
