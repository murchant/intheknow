# intheknow

 Project completed as dissertation for Masters degree.
## Overview
This project aimed to determine the extent supervised machine learning techniques could be used to predict the accuracy of tweets in relation to football transfers.

  **IMPORTANT:** ALL CODE CAN BE TAILORED TO YOUR SPECIFIC TWEET GATHERING, LABELLING AND CLASSIFICATION NEEDS.

## Breakdown

  Project three distinct sections.
  - Stage 1: Data Gathering
  - Stage 2: Data Labelling
  - Stage 2: Classification Experiments


  | module | stage | description |
  | :-----: |:----:| :-----:|
  | kb_builder.py | 1 | build database of known transfers |
  | get_tweets.py | 1 | get transfer tweets  |
  | db.py | 1/2/3 | build db collections|
  | relations.py | 1 |  create queries for GetOldTweets   |
  | ner.py | 1/2/3 | label tweets using Named Entity Recognition (NER) |
  | data_checking.py | 1/2/3 | script for checking db values etc|

  Tweet gathering done using [GetOldTweets](https://github.com/Jefferson-Henrique/GetOldTweets-python). **Free** workaround to Twitters expensive API. Clone this repo into top directory.

## Classification

Two approaches, as implemented in **classification.ipynd:**
1. td-idf encoded n-grams of tweets for input features. Simple MLP model.
2. Word vectorisation, semantics embedding layer, Separated Convolution Neural Network.
