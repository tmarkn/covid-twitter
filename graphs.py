import json
import datetime
import numpy as np
import dateutil.parser
import operator
import pytz
import matplotlib.pyplot as plt

def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')

# turn save to True to save the graphs as .png images
save = False
filePath='data/twitter.json'
localTweetList = []
globalTweetCounter = 0
frequencyMap = {}
people = {}
timeFormat = "%a %b %d %H:%M:%S +0000 %Y"
with open(filePath, 'r') as f:
    tweets = json.loads(f.readline())
    for tweet in tweets:
        # Try to extract the time of the tweet
        currentTime = dateutil.parser.parse(tweet['created_at'])
        currentTime = currentTime.replace(hour=0, minute=0, second=0)

        # print(currentTime)
        # Increment tweet count
        globalTweetCounter += 1
        
        # If our frequency map already has this time, use it, otherwise add
        if currentTime in frequencyMap.keys():
            timeMap = frequencyMap[currentTime]
            timeMap["count"] += 1
            timeMap["list"].append(tweet)
        else:
            frequencyMap[currentTime] = {"count":1, "list":[tweet]}

        # If our user is already added, use, otherwise add
        if tweet['user']['screen_name'] in people:
            people[tweet['user']['screen_name']].append(tweet)
        else:
            people[tweet['user']['screen_name']] = [tweet]

# sort words before first reported case of Covid-19 2020-01-21
# adjust times to utc
utc = pytz.UTC
targetTime = utc.localize(dateutil.parser.parse('2020-01-21'))
wordsBefore = {}
wordsAfter = {}
for person in people:
    print(person, len(people[person]))
    # count number of words used
    wordsBefore[person] = {}
    wordsAfter[person] = {}
    for tweet in people[person]:
        # split text and clean words
        tempWords = tweet['text'].split()
        tempWords = [deEmojify(i).strip().lower() for i in tempWords]
        # check if before or after first case of covid and add to dictionary
        timeCreated = dateutil.parser.parse(tweet['created_at'])
        timeCreated = timeCreated.replace(hour=0, minute=0, second=0)

        # before first case
        if timeCreated < targetTime:
            for word in tempWords:
                if not word:
                    continue
                if word in wordsBefore[person]:
                    wordsBefore[person][word] += 1
                else:
                    wordsBefore[person][word] = 1
        # after first case 
        else:
            for word in tempWords:
                if not word:
                    continue
                if word in wordsAfter[person]:
                    wordsAfter[person][word] += 1
                else:
                    wordsAfter[person][word] = 1

    # remove noisey words
    entriesToRemove = ('the', 'and', 'to', 'of', 'a', 'an', 'are', 'in', 'is', 'on')
    
    adjustedBefore = wordsBefore
    adjustedAfter = wordsAfter

    for k in entriesToRemove:
        adjustedBefore[person].pop(k, None)
        adjustedAfter[person].pop(k, None)

    # sort words
    adjustedBefore[person] = sorted(adjustedBefore[person].items(), key=lambda item: item[1], reverse=True)
    adjustedAfter[person] = sorted(adjustedAfter[person].items(), key=lambda item: item[1], reverse=True)

    print('\t', adjustedBefore[person][:10])
    print('\t', adjustedAfter[person][:10])

    # plot graphs
    fig, ax = plt.subplots()
    fig.set_size_inches(18,6)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.15)
    plt.subplot(1, 2, 1)
    
    plt.title("Word Frequency: " + person + " (Before First Case of Covid: 2020-01-21)")
    plt.xticks(rotation=45, ha="right") 
    plt.bar([x[0] for x in adjustedBefore[person]][:30], [x[1] for x in adjustedBefore[person]][:30], color='blue', label='Word Frequency')
    

    plt.subplot(1, 2, 2)
    plt.title("Word Frequency: " + person + " (After First Case of Covid: 2020-01-21)")
    plt.xticks(rotation=45, ha="right") 
    plt.bar([x[0] for x in adjustedAfter[person]][:30], [x[1] for x in adjustedAfter[person]][:30], color='red', label='Word Frequency')
    ax.legend()
    if save == True:
        plt.savefig("graphs/" + person + ".png", bbox_inches='tight')
    plt.show()

# Fill in any gaps
times = sorted(frequencyMap.keys())
firstTime = times[0]
lastTime = times[-1]
thisTime = firstTime

timeIntervalStep = datetime.timedelta(hours=24)
while ( thisTime <= lastTime ):
    if ( thisTime not in frequencyMap.keys() ):
        frequencyMap[thisTime] = {"count":0, "list":[]}
        
    thisTime = thisTime + timeIntervalStep

print ("Processed Tweet Count:", globalTweetCounter)

fig, ax = plt.subplots()
fig.set_size_inches(10,4)
fig.tight_layout()
fig.subplots_adjust(bottom=0.3)

plt.title("Tweet Frequency (First case of COVID-19 at 2020-01-21)")

# Sort the times into an array for future use
sortedTimes = sorted(frequencyMap.keys())

# What time span do these tweets cover?
print ("Time Frame:", sortedTimes[0], sortedTimes[-1])

# Get a count of tweets per minute
postFreqList = [frequencyMap[x]["count"] for x in sortedTimes]

# We'll have ticks every 10 days
smallerXTicks = range(0, len(sortedTimes), 10)
plt.xticks(smallerXTicks, [sortedTimes[x].strftime('%Y:%m:%d') for x in smallerXTicks], rotation=45, ha="right")

# Plot the post frequency
ax.plot(range(len(frequencyMap)), [x if x > 0 else 0 for x in postFreqList], color="blue", label="Posts")
ax.grid(b=True, which=u'major')
ax.legend()
if save == True:
    plt.savefig("graphs/tweetFreq.png", bbox_inches='tight')
plt.show()

# covid data
covid = np.loadtxt("data/us-counties.csv", delimiter=",", dtype='str')
covid = np.delete(covid, (0), axis=0)
cases = {}
for time in sortedTimes:
    cases[time] = 0

count = 0
for reported in covid:
    # print(reported)
    time = utc.localize(dateutil.parser.parse(reported[0]))
    count += int(reported[4])
    # print(reported[4])
    cases[time] = count
    # print(cases[time])

# print(len(cases))
# print(len(frequencyMap))
# print(count)
# for k in cases:
#     print(k, cases[k])

postCaseList = np.array([cases[x] for x in cases])
# print(postCaseList)

fig2, ax2 = plt.subplots()
fig2.set_size_inches(10,4)
fig2.tight_layout()
fig2.subplots_adjust(left=0.1, bottom=0.3)
plt.title("Reported Cases of COVID-19 (First case at 2020-01-21)")
plt.xticks(smallerXTicks, [sortedTimes[x].strftime('%Y:%m:%d') for x in smallerXTicks], rotation=45, ha="right")
ax2.plot(range(len(sorted([k for k in cases]))), postCaseList, color="red", label='Reported Cases')
ax2.grid(b=True, which=u'major')
ax2.legend()
if save == True:
    plt.savefig("graphs/reportedCases.png", bbox_inches='tight')
plt.show()

# A map for hashtag counts
hashtagCounter = {}

# For each minute, pull the list of hashtags and add to the counter
for t in sortedTimes:
    timeObj = frequencyMap[t]
    
    for tweet in timeObj["list"]:
        hashtagList = tweet["entities"]["hashtags"]
        
        for hashtagObj in hashtagList:
            
            # We lowercase the hashtag to avoid duplicates (e.g., #MikeBrown vs. #mikebrown)
            hashtagString = hashtagObj["text"].lower()
            
            if ( hashtagString not in hashtagCounter ):
                hashtagCounter[hashtagString] = 1
            else:
                hashtagCounter[hashtagString] += 1

print ("Unique Hashtags:", len(hashtagCounter.keys()))
sortedHashtags = sorted(hashtagCounter, key=hashtagCounter.get, reverse=True)
# print ("Top Twenty Hashtags:")
# for ht in sortedHashtags[:20]:
#     print ("\t", "#" + ht, hashtagCounter[ht])

fig, ax = plt.subplots()
fig.set_size_inches(10,4)
fig.subplots_adjust(bottom=0.3)
plt.title("Hashtag Count")
plt.xticks(range(20), [ht for ht in sortedHashtags][:20], rotation=45, ha="right")
ax.bar(range(20), [hashtagCounter[ht] for ht in sortedHashtags][:20], color="red", label='Hashtags')
ax.grid(b=True, which=u'major')
ax.legend()
if save == True:
    plt.savefig("graphs/hashtags.png", bbox_inches='tight')
plt.show()