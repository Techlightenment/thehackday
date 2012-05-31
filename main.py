import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import json
import stream
import threading
import time

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
    waiters = set()

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self):
        BigGraphSocketHandler.waiters.add(self)

    def on_close(self):
        BigGraphSocketHandler.waiters.remove(self)

    @classmethod
    def handle(cls, timestamp, msg, sentiment, hashtag):
        for waiter in cls.waiters:
            pass
            #waiter.write_message(json.dumps(data))


class SmallGraphSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = {}
    positive_scores = {}
    negative_scores = {}

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self):
        hashtag = self.get_argument('hashtag')
        SmallGraphSocketHandler.waiters.setdefault(hashtag, set()).add(self)

    def on_close(self):
        for vs in SmallGraphSocketHandler.waiters.values():
            try:
                vs.remove(self)
            except KeyError:
                pass

    @classmethod
    def handle(cls, timestamp, msg, sentiment, hashtag):

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
    def handle(cls, timestamp, msg, sentiment, hashtag):
        for waiter in cls.waiters.get(hashtag, []):
            waiter.write_message(json.dumps((timestamp, msg)))


class TweetDaemon(object):
    stop_tweet_daemon = False
    WORDS = ['jubilee', 'olympics', 'euro2012', 'london2012']

    @classmethod
    def run(cls):
        for tweet in stream.tweets(cls.WORDS):
            if cls.stop_tweet_daemon: break
            SmallGraphSocketHandler.handle(*tweet)
            #BigGraphSocketHandler.handle(*tweet)
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
