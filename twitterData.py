import tweepy
import json
from datetime import datetime
from os import path

import cred

auth = tweepy.OAuthHandler(cred.CONSUMER_KEY, cred.CONSUMER_SECRET)
auth.set_access_token(cred.ACCESS_TOKEN, cred.ACCESS_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True)

usernames = ['jimmyfallon',
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
                'realdonaldtrump',
                'theellenshow',
                'ladygaga',
                'critiano',
                'taylorswift13',
                'rihanna',
                'katyperry',
                'justinbieber',
                'barackobama']
startDate = datetime(2019, 9, 1, 0, 0, 0)
endDate = datetime(2020, 3, 31, 0, 0, 0)

tweets = []
for username in usernames:
    print(username)
    tmpTweets = api.user_timeline(username)
    for tweet in tmpTweets:
        if tweet.created_at < endDate and tweet.created_at > startDate:
            tweets.append(tweet)
    while (tmpTweets[-1].created_at > startDate):
        tmpTweets = api.user_timeline(username, max_id = tmpTweets[-1].id)
        for tweet in tmpTweets:
            if tweet.created_at < endDate and tweet.created_at > startDate and tweet.lang == 'en':
                tweets.append(tweet)
                print(tweet.text)
print(len(tweets))

with open('data.json') as f:
    json.dump(tweets, f)