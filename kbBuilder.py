import urllib2
from bs4 import BeautifulSoup

quote_page = 'https://en.wikipedia.org/wiki/List_of_English_football_transfers_summer_2017'
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
loans=[]

while(windowT<len(transAr)):
    transfers.append([transAr[windowT], transAr[windowT+1],transAr[windowT+2],transAr[windowT+3],transAr[windowT+4]])
    windowT+=5

while(windowL<len(loansAr)):
    loans.append([loansAr[windowL], loansAr[windowL+1],loansAr[windowL+2],loansAr[windowL+3]])
    windowL+=4

print(transfers[len(transfers)-1])
print(loans[len(loans)-1])
