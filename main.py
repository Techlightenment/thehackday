import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import json
import stream
import threading

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/biggraph",      BigGraphSocketHandler),
            (r"/smallgraph",    SmallGraphSocketHandler),
            (r"/tweets",        TweetsSocketHandler),
        ]
        settings = dict(
            cookie_secret="43oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class BigGraphSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = {}
    scores = {}
    groups = {}


    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self):

        hashtags = self.get_argument('hashtag').split(',')

        for h in hashtags:
            try:
                del BigGraphSocketHandler.scores[h]
            except KeyError: pass
            try:
                del BigGraphSocketHandler.groups[h]
            except KeyError: pass

        # Given any hashtag returns its group
        for h in hashtags:
            BigGraphSocketHandler.groups[h] = hashtags

        for h in hashtags:
            BigGraphSocketHandler.waiters.setdefault(h, set()).add(self)

    def on_close(self):
        for vs in BigGraphSocketHandler.waiters.values():
            try:
                vs.remove(self)
            except KeyError:
                pass

    @classmethod
    def handle(cls, timestamp, msg, sentiment, hashtag, author_url):

        # Ignore tweets with neutral (0) sentiment
        if sentiment == 0:
            return

        # Get scores for all hashtags in the group.
        xs = BigGraphSocketHandler.scores.get(hashtag, [])
        xs.append(sentiment)
        xs = xs[-10:]

        # Get average sentiment
        def get_average(hashtag):
            xs = BigGraphSocketHandler.scores.get(hashtag, [])
            delimiter = sum(map(abs, xs))
            if delimiter:
                av = sum(xs) / delimiter
            else:
                av = 0
            return av

        # Calculate avergage
        scores = []
        for h in BigGraphSocketHandler.groups[hashtag]:
            scores.append(get_average(h))      

        for waiter in cls.waiters.get(hashtag, []):
            waiter.write_message(json.dumps(scores))


class SmallGraphSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = {}
    positive_scores = {}
    negative_scores = {}

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self):

        hashtag = self.get_argument('hashtag')

        try:
            del SmallGraphSocketHandler.positive_scores[hashtag]
        except KeyError: pass
        try:
            del SmallGraphSocketHandler.negative_scores[hashtag]
        except KeyError: pass

        SmallGraphSocketHandler.waiters.setdefault(hashtag, set()).add(self)

    def on_close(self):
        for vs in SmallGraphSocketHandler.waiters.values():
            try:
                vs.remove(self)
            except KeyError:
                pass

    @classmethod
    def handle(cls, timestamp, msg, sentiment, hashtag, author_url):

        # Ignore tweets with neutral (0) sentiment
        if sentiment == 0:
            return

        # Maintain sentiment.
        if sentiment > 0:
            cls.positive_scores[hashtag] =\
                cls.positive_scores.get(hashtag, 0) + sentiment
        else:
            cls.negative_scores[hashtag] =\
                cls.negative_scores.get(hashtag, 0) + abs(sentiment)
        
        # Get current sentiment score.
        scores = (cls.positive_scores.get(hashtag, 0),
                  cls.negative_scores.get(hashtag, 0))

        for waiter in cls.waiters.get(hashtag, []):
            waiter.write_message(json.dumps(scores))


class TweetsSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = {}

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self):
        hashtag = self.get_argument('hashtag')
        TweetsSocketHandler.waiters.setdefault(hashtag, set()).add(self)

    def on_close(self):
        for vs in TweetsSocketHandler.waiters.values():
            try:
                vs.remove(self)
            except KeyError:
                pass

    @classmethod
    def handle(cls, timestamp, msg, sentiment, hashtag, author_url):
        
        # Ignore tweets with neutral (0) sentiment
        if sentiment == 0:
            return

        if sentiment > 0:
            sentiment_bool = True
        else:
            sentiment_bool = False

        for waiter in cls.waiters.get(hashtag, []):
            waiter.write_message(json.dumps((
                sentiment_bool, timestamp, msg, author_url)))


class TweetDaemon(object):
    stop_tweet_daemon = False
    WORDS = ['jubilee', 'olympics', 'philpott', 'chocolate']

    @classmethod
    def run(cls):
        for tweet in stream.tweets(cls.WORDS):
            if cls.stop_tweet_daemon: break
            SmallGraphSocketHandler.handle(*tweet)
            BigGraphSocketHandler.handle(*tweet)
            TweetsSocketHandler.handle(*tweet)

def main():

    tweet_daemon = threading.Thread(target=TweetDaemon.run)
    tweet_daemon.start()

    app = Application()
    app.listen(8888)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        TweetDaemon.stop_tweet_daemon = True
        tweet_daemon.join()


if __name__ == "__main__":
    main()
