import tweepy
import json
import time
from datetime import datetime
from os import path

import cred

auth = tweepy.OAuthHandler(cred.CONSUMER_KEY, cred.CONSUMER_SECRET)
auth.set_access_token(cred.ACCESS_TOKEN, cred.ACCESS_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

usernames = [
    'billgates', #21st
    'jimmyfallon',
    'shakira',
    'narendramodi',
    'britneyspears',
    'cnnbrk',
    'twitter',
    'selenagomez',
    'kimkardashian',
    'jtimberlake',
    'arianagrande',
    'youtube',
    # 'realdonaldtrump', #api problems with this one
    'theellenshow',
    'ladygaga',
    'cristiano',
    'taylorswift13',
    'rihanna',
    'katyperry',
    'justinbieber',
    'barackobama', #1st
]
# 15 days before
# startDate = datetime(2019, 8, 17, 0, 0, 0)
# endDate = datetime(2019, 8, 31, 0, 0, 0)

# target dataset
startDate = datetime(2019, 9, 1, 0, 0, 0)
endDate = datetime(2020, 3, 31, 0, 0, 0)

# 15 days after
# startDate = datetime(2020, 4, 1, 0, 0, 0)
# endDate = datetime(2020, 4, 15, 0, 0, 0)


allTweets = []
for username in usernames:
    print(username)
    tweets = []
    tmpTweets = api.user_timeline(username, count = 200)
    for tweet in tmpTweets:
        if tweet.created_at < endDate and tweet.created_at > startDate and tweet.lang == 'en':
            tweets.append(tweet._json)

    prev = tmpTweets[-1]
    while (tmpTweets[-1].created_at > startDate):
        print("Last Tweet @", tmpTweets[-1].created_at, "- fetching some more")
        tmpTweets = api.user_timeline(username, max_id = tmpTweets[-1].id, count = 200)

        for tweet in tmpTweets:
            if tweet.created_at < endDate and tweet.created_at > startDate and tweet.lang == 'en':
                tweets.append(tweet._json)
    print(len(tweets))
    allTweets += tweets

with open('data/twitterBefore.json','w') as f:
    json.dump(allTweets, f)