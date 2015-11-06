#!/usr/bin/python
# -*- coding: utf-8 -*-
import config
import torndb
import tornado
from tornado.web import Application, RequestHandler, os

__author__ = 'nekocode'


class DB:
    def __init__(self):
        self.user_id = None
        self.db = torndb.Connection(config.DB_HOST, config.DB_NAME, config.DB_USER, config.DB_PWD)

    def login(self, name, pwd):
        return self.db.get("select * from users where username='%s' and password='%s'" % (name, pwd))

    def get_school_accounts(self):
        return self.db.query("select * from school_accounts where admin_id='%s'" % self.user_id)

    def get_vote_accounts(self):
        return self.db.query("select * from vote_accounts where admin_id='%s'" % self.user_id)

db = None


class BaseHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get_current_user(self):
        return self.get_secure_cookie("user")


class VoteAccountsHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        name = tornado.escape.xhtml_escape(self.current_user)
        self.write("Hello, " + name)


class LoginHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        if not self.current_user:
            self.render("static/admin/login.html")

        else:
            self.redirect('/vote_accounts', permanent=True)

    def post(self):
        name = self.get_argument("name")
        pwd = self.get_argument("pwd")

        global db
        rlt = db.login(name, pwd)

        if rlt is None:
            self.write(u"登陆失败，请尝试刷新页面重新登陆")

        else:
            self.set_secure_cookie("user", name)
            self.redirect('/vote_accounts', permanent=True)


if __name__ == '__main__':
    db = DB()

    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret": "61oETzKXQAGaYdk12345GeJJFuYh7EQnp2XdTP1o/Vo=",
        "login_url": "/login",
    }

    application = Application([
        (r'/', tornado.web.RedirectHandler, {"url": "/login", "permanent": False}),
        (r"/login", LoginHandler),
        (r"/vote_accounts", VoteAccountsHandler),
    ], **settings)

    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()

