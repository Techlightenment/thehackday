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
    def dispatch(cls, data):
        for waiter in cls.waiters:
            waiter.write_message(json.dumps(data))


class SmallGraphSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self):
        SmallGraphSocketHandler.waiters.add(self)

    def on_close(self):
        SmallGraphSocketHandler.waiters.remove(self)

    @classmethod
    def dispatch(cls, data):
        for waiter in cls.waiters:
            waiter.write_message(json.dumps(data))


class TweetsSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self):
        TweetsSocketHandler.waiters.add(self)

    def on_close(self):
        TweetsSocketHandler.waiters.remove(self)

    @classmethod
    def dispatch(cls, data):
        for waiter in cls.waiters:
            waiter.write_message(json.dumps(data))


class TweetDaemon(object):
    stop_tweet_daemon = False

    @classmethod
    def run(cls):
        for tweet in stream.tweets(['jubilee', 'olympics', 'euro2012', 'london2012']):
            if cls.stop_tweet_daemon: break
            BigGraphSocketHandler.dispatch({'tweet': tweet})


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
