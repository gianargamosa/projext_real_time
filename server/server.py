import os
import threading
import tornado.options
import tornado.ioloop
import tornado.httpserver
import tornado.httpclient
import tornado.web
from tornado import gen
from tornado.web import asynchronous

tornado.options.define('port', type=int, default=8800, help='server port number (default: 9000)')
tornado.options.define('debug', type=bool, default=False, help='run in debug mode with autoreload (default: False)')

class Worker(threading.Thread):
   def __init__(self, callback=None, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)
        self.callback = callback

   def run(self):
        import time
        time.sleep(10)
        self.callback('DONE')

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/thread", ThreadHandler),
        ]
        settings = dict(
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            debug = tornado.options.options.debug,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class IndexHandler(tornado.web.RequestHandler):
    client = tornado.httpclient.AsyncHTTPClient()

    @asynchronous
    @gen.engine
    def get(self):
        response = yield gen.Task(self.client.fetch, "http://google.com")

        self.finish("Google's homepage is %d bytes long" % len(response.body))

class ThreadHandler(tornado.web.RequestHandler):
    @asynchronous
    def get(self):
        Worker(self.worker_done).start()

    def worker_done(self, value):
        self.finish(value)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()