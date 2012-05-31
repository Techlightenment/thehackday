import re
import tweetstream
import time

filename = 'wordlist.txt'
wordmap = dict(map(lambda (w,s): (w, int(s)), [ws.strip().split('\t') for ws in open(filename)]))
word_split = re.compile(r"\W+")

def sentiment(text):
    words = word_split.split(text.lower())
    sentiments = [score for score in map(lambda word: wordmap.get(word, 0), words) if score]
    if sentiments:
        sentiment = float(sum(sentiments))
    else:
        sentiment = 0
    return sentiment

def category(text, words):
    text_lower = text.lower()
    for word in words:
        if word.lower() in text_lower:
            return word 

def tweets(words):
    t = tweetstream.FilterStream('tl_hackday', 'h@ckd@yh@ckd@y', track=words)
    for tweet in t:
        text = tweet['text']
        sent = sentiment(text)
        cat = category(text, words)
        if not cat:
            continue
        ts = int(time.time())
        yield ts, text, sent, cat

if __name__ == '__main__':
    for v in tweets(['olympics', 'jubilee']):
        print v
