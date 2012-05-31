import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import json

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/feed", FeedHandler),
            (r"/biggraph", BigGraphSocketHandler),
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


class FeedHandler(tornado.web.RequestHandler):
    def get(self):
        BigGraphSocketHandler.dispatch({'msg': 'hello world'})
        self.write('ok')


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


def main():
    app = Application()
    app.listen(8888)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
