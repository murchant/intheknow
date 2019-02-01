import urllib2
from bs4 import BeautifulSoup
import csv


def main():
    info2018 = get_transfers('https://en.wikipedia.org/wiki/List_of_English_football_transfers_summer_2018')
    transfers_eighteen = info2018["transfers"]
    loans_eighteen = info2018["loans"]
    info2017 = get_transfers('https://en.wikipedia.org/wiki/List_of_English_football_transfers_summer_2017')
    transfers_seventeen = info2017["transfers"]
    loans_seventeen = info2017["loans"]
    write_info(transfers_eighteen, "transfers2018.csv")
    write_info(loans_eighteen, "loans2018.csv")
    write_info(transfers_seventeen, "transfers2017.csv")
    write_info(loans_seventeen, "loans2017.csv")


def write_info(info, name):
    with open(name, mode='w') as info_file:
        info_writer = csv.writer(info_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in info:
            info_writer.writerow(i)
    return 1


def get_transfers(qPage):
    quote_page = qPage
    page = urllib2.urlopen(quote_page)
    soup = BeautifulSoup(page, 'html.parser')

    ar = soup.find_all('tbody')
    textTransfer = ar[0].text.strip()
    textLoans = ar[1].text.strip()
    transAr = textTransfer.split('\n\n')
    loansAr = textLoans.split('\n\n')
    windowT = 0
    windowL = 0
    transfers = []
    loans = []

    while(windowT < len(transAr)):
        transfers.append([transAr[windowT].encode('utf-8'),  transAr[windowT+1].encode('utf-8'), transAr[windowT+2].encode('utf-8'), transAr[windowT+3].encode('utf-8'), transAr[windowT+4].encode('utf-8')])
        windowT += 5

    while(windowL < len(loansAr)):
        loans.append([loansAr[windowL].encode('utf-8'), loansAr[windowL+1].encode('utf-8'), loansAr[windowL+2].encode('utf-8'), loansAr[windowL+3].encode('utf-8')])
        windowL += 4

    return {"transfers": transfers, "loans": loans}


if __name__ == '__main__':
    main()
