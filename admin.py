#!/usr/bin/python
# -*- coding: utf-8 -*-
import config
import torndb
import tornado
from tornado.web import Application, RequestHandler, os

db = None
PER_PAGE_ROWS = 1


class BaseHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get_current_user(self):
        return self.get_secure_cookie("user")


class VoteAccountsHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        global db
        userid = int(tornado.escape.xhtml_escape(self.current_user))
        p = int(self.get_argument('p', 1))
        lid = int(self.get_argument('lid', 1))

        # 获取分页数量
        row_count = db.get("select count(*) from vote_accounts where admin_id=%d" % userid)['count(*)']
        page_count = row_count/PER_PAGE_ROWS + 1
        if row_count % PER_PAGE_ROWS == 0:
            page_count -= 1

        if p < 1 or p > page_count:
            p = 1

        if page_count <= 5:
            pages = range(1, page_count+1)
        else:
            if p <= 3:
                pages = range(1, 6)
            elif p > page_count-2:
                pages = range(page_count-4, page_count+1)
            else:
                pages = range(p-2, p+2)

        # 获取分页
        rows = db.query("select * from vote_accounts where admin_id=%d "
                        "order by auto_id desc limit %d,%d"
                        % (userid, lid - PER_PAGE_ROWS + 1, PER_PAGE_ROWS))

        # 使用 lid 来优化分页
        c = len(rows)
        if c > 0:
            lid = rows[c-1].id

        self.render("static/admin/vote-accounts.html", rows=rows, pages=pages, p=p, lid=lid)


class SubAccountsHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.render("static/admin/sub-accounts.html")


class ClassesHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.render("static/admin/classes.html")


class PeopleHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.render("static/admin/people.html")


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
        rlt = db.get("select * from users where username='%s' and password='%s'" % (name, pwd))

        if rlt is None:
            self.write(u"登陆失败，请尝试刷新页面重新登陆")

        else:
            self.set_secure_cookie("user", str(rlt.id))
            self.redirect('/vote_accounts', permanent=True)


if __name__ == '__main__':
    db = torndb.Connection(config.DB_HOST, config.DB_NAME, config.DB_USER, config.DB_PWD)

    import uimodules
    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "cookie_secret": "61oETzKXQAGaYdk12345GeJJFuYh7EQnp2XdTP1o/Vo=",
        "login_url": "/login",
        "ui_modules": uimodules,
    }

    application = Application([
        (r'/', tornado.web.RedirectHandler, {"url": "/login", "permanent": False}),
        (r"/login", LoginHandler),
        (r"/vote_accounts", VoteAccountsHandler),
        (r"/sub_accounts", SubAccountsHandler),
        (r"/classes", ClassesHandler),
        (r"/people", PeopleHandler),
    ], **settings)

    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()

