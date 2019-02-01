# Step by step
Step by step notes on what was done at each stage of dissertation.

## Knowledge Base
Knowledge Base was created to store a collection of known successful transfers and loans from previous transfer windows.

20th- 24th January:
- BeautifulSoup (https://www.crummy.com/software/BeautifulSoup/bs4/doc/) python library used to scrape wikipedia page of completed transfers (eg: 'https://en.wikipedia.org/wiki/List_of_English_football_transfers_summer_2018')
- Wrote methods to get transfers and loan data and wirte it to CSV file.


## Rumour Retrieval

- Rumour retrieval used using tool getOldTweets python (https://github.com/Jefferson-Henrique/GetOldTweets-python).
- Allows me to retrieve tweets from present day all the way back to twitters origins.
- Initial query terms used like "#intheknow", "transfer deadline day" too generic. Lot of "noise", would lead to a lot of cleaning the data.
- **Solution:** Define player to club relationships and label as know *true* or *false* transfer. Use these player to club relationships as query terms with declared synonyms.
- TODO:
  - declare synonyms
  - declare method of generating the relationships
  - generate true relationships
  - false relationships (false harder as you've to come up with realistic transfer relationships, that didn't happen. What defines realistic though.. see).
  - Retrieve rumour

### Rumour retrieval method 1:
  - define synonyms
  - define true query terms
  - retrieve data set using terms
  - use true relationships to retrieve rumours which are false. (ie: contains player name but wrong destination club)

- **created relations.py:** generates true and false player and club relationships, and generates query search terms for said relationships

- **created getTweets.py:** uses query terms to execute shell command and retrieve tweets.