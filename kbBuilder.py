import urllib2
from bs4 import BeautifulSoup

quote_page = 'https://en.wikipedia.org/wiki/List_of_English_football_transfers_summer_2018'
page = urllib2.urlopen(quote_page)
soup = BeautifulSoup(page, 'html.parser')

ar = soup.find_all('tbody')
textTransfer = ar[0].text.strip()
textLoans = ar[1].text.strip()
textTransAr = textTransfer.split('\n\n')
textLoanAr = textLoans.split('\n\n')

windowT = 0
windowL = 0
transfers = []
loans=[]

while(windowT<len(textTransAr)):
    transfers.append([textTransAr[windowT], textTransAr[windowT+1],textTransAr[windowT+2],textTransAr[windowT+3],textTransAr[windowT+4]])
    windowT+=5

while(windowL<len(textLoanAr)):
    loans.append([textLoanAr[windowL], textLoanAr[windowL+1],textLoanAr[windowL+2],textLoanAr[windowL+3]])
    windowL+=4

print(transfers[len(transfers)-1])
print(loans[len(loans)-1])
