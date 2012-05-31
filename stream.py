import re
import tweetstream

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

def run(words):
    t = tweetstream.FilterStream('tl_hackday', 'h@ckd@yh@ckd@y', track=words)
    for tweet in t:
        text = tweet['text']
        print text
        print "sentiment: %s" % sentiment(text)

if __name__ == '__main__':
    run(['olympics', 'jubilee', 'euro2012', 'london2012'])
