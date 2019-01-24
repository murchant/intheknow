import urllib2
from bs4 import BeautifulSoup

quote_page = 'https://en.wikipedia.org/wiki/List_of_English_football_transfers_summer_2018'
page = urllib2.urlopen(quote_page)
soup = BeautifulSoup(page, 'html.parser')

ar = soup.find('tbody')
textTransfer = ar.text.strip()
textAr = textTransfer.split('\n\n')

window = 0
transfers = []

while(window<len(textAr)):
    transfers.append([textAr[window], textAr[window+1],textAr[window+2],textAr[window+3],textAr[window+4]])
    window+=5

print transfers[len(transfers)-1]
