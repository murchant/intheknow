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

#### True Rumour
- **created relations.py:** generates true and false player and club relationships, and generates query search terms for said relationships

- **created getTweets.py:** uses query terms to execute shell command and retrieve tweets.

- **created dataCheck.py:** uses query terms to execute shell command and retrieve tweets.

  - cmds.txt is run as base script and runs 20 queries at a time
  - club synonym.
  - player relationship with just *to club* and *player*.
  - Defined shorter queries, composed of payer and linked club.
  - *Interesting:* Data frame for shorter queries was over twice that of longer queries
    - 2018: Shorter: 44220 Longer: 19081
    - Intersection of the two is 14602
    - Therefore over 75% longer are present in shorter but still worth querying.
    - Outer join (outer merge pandas) gives us combined set of true tweets no duplicates of 46750. (*new numbers since this recording*)
    - "Up to" date set to day they signed for club (maybe set it to day before)

#### Entity Recognition
- **Created ner.py:** Uses SpaCy for entity recognition.
- Processes tweet text and extracts entities from them. Does further processing to check whether claim came true or not, then stores in database with label accordingly.
- First round (*runtime*: approx 2.5 hrs): 2726/8267 were labelled. Conducted on true set.
    - **Reason:** SpaCy having trouble defining Zlatan as person. (GPE, ORG). Also *Zlatan* more commonly used that his full name.
    - **Possible Solution:** check for players as ORG's and GPE's as well. Clubs wrongfully identified will be disregarded on DB check. But still all Zlatan tweets, hence such a large skew in successful labels.
    - **Second name solution:** have a player to name synonym collection. Most simple form: *use just second name a query*.
- Second round (*runtime*: started @ 2.5hrs ): 5564/8267

#### DataBase setup:
- **Created db.py**
- Running mongodb as local store
- Created true rels store
- transferdb:
    - player database
    - true transfers database
    - clubdb

#### False Rumour
- Theory:
    - Have collection of know true rumours.
    - Use this data to retrieve accounts which tweet the most about transfer rumours.
    - Use them and find most frequently occurring transfer rumours (Zipf distribution implementation possibly)
    - Retrieve tweet from that account:
          - If (not already known true) & (contains player mapped to club) & (not in known true transfers):
                fake_collection.add(rumour tweet)
- **relations.py updates:** functions to receive top football tweeting accounts and to and commands to receive their tweets within a period. Run 1 false_cmds.txt: (12:05 - 1:30 ish)

- **process_tweet() run 1:**
      - Labelled true before 5564/8267.
      - Labelled false before 0/22731 possibles.
      - start @ 2:20
    - **STOPPED** due to staggering amount of false false's.
      - clubs synonyms ✅ fixed club_syn db
      - tweets talking about *"rejected transfers"*
      - SpaCy not **recognising** clubs eg: "Reading", "Colchester united", "Barnsley", "Swansea", "Morecambe", "Middlesbrough"
      - **Hashtags** were being interpreted as money, so made hashtag_remover()
      - **Duplicate** entries into db eg (Jordan Williams from Liverpool and Jordan Williams from Huddersfield town) *solution:* (not that big of deal and can just do a run through of every duplicates at end)

- **process_tweet() run 2:**
      - 5678/6274 labelled false
      - Manually sampled 100.... 34/100 were wrongly labelled false due to reasons explained above.
      - Problems:
      - Worlds cup teams
            - world cup news
            - Contract renewals
            - Manager appointing
            - Leaving club, to a club but not both clubs listed.
            - Negatives eg : Barcelona not interested in signing
            - Vague tweets, “Barcelona are looking for a midfielder”
            - Loan deals (easy fix just include loan data)
            - Unveiled new kit.
            - Europa, Champions draw
            - Starting XI, 15

            Note: A lot of reporting like this “Roma sporting director Monchi has insisted the club have not received any offers for goalkeeper Alisson Becker. The Brazilian international is reportedly a summer transfer target for Real Madrid and Liverpool, but the Italian club have rejected this talk” But even though its reporting, what the report is implying is false.

- **process_tweet() run 3:**
      - Difference = *noise_filter*, filter out world cups news, manger news, contract negotiations.
      - 13:30 - 16:00. Stopped at 8259 due to trying to perform .replace() on float.
      - 7455/8259 labelled false
      - Club Probelms:
          - West Ham united

- **switch up, cause too much noise in data**
- **new method:** retrieve tweets from top true tweeters and filter those to transfer news based on terms.
- *Retrained* spacy english model to include club names and players which were not present before. very tedious.
- Added retraining methods
