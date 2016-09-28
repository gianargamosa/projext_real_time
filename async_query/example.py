#!/usr/bin/env python

from os import path

import tornado.options
import tornado.web
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options

import psycopg2

from async_psycopg2 import Pool


define('port', default=8888, help='run on the given port', type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r'/test1', Test1Handler),
            (r'/test2', Test2Handler)
        ]
        settings = dict(
            template_path=path.join(path.dirname(__file__), 'templates'),
            static_path=path.join(path.dirname(__file__), 'static'),
            xsrf_cookies=True,
            cookie_secret='dsfretghj867544wgryjuyki9p9lou67543/Vo=',
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = None


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        if not self.application.db:
            self.application.db = Pool(1, 20, 10, **{
                'host': 'localhost',
                'database': 'infuna_db',
                'user': 'infuna',
                'password': 'password',
                'async': 1
            })
        return self.application.db


class MainHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.db.execute('SELECT 42, 12, 40, 11;', callback=self._on_response)

    def _on_response(self, cursor):
        print 'Request', cursor.fetchall()
        self.write('Hello, world')
        self.finish()


class Test1Handler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.db.execute('SELECT pg_sleep(15); SELECT 5454, 324, 2343;',
            callback=self._on_response)

    def _on_response(self, cursor):
        print 'Request', cursor.fetchall()
        cursor.close()
        self.write('Test 1')
        self.finish()


class Test2Handler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.db.execute('SELECT pg_sleep(15); SELECT 636, 222, 123;',
            callback=self._on_response)

    def _on_response(self, cursor):
        print 'Request', cursor.fetchall()
        cursor.close()
        self.write('Test 2')
        self.finish()


def main():
    try:
        tornado.options.parse_command_line()
        http_server = HTTPServer(Application())
        http_server.bind(8888)
        http_server.start(0) # Forks multiple sub-processes
        IOLoop.instance().start()
    except KeyboardInterrupt:
        print 'stopping process ...'

if __name__ == '__main__':
    main()
