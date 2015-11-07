#!/usr/bin/python
# -*- coding: utf-8 -*-
import config
import torndb
import tornado
from tornado.web import Application, RequestHandler, os

db = None
PER_PAGE_ROWS = 2


def get_page_rows(p, table_name, where=''):
    global db

    # 获取分页数量
    row_count = db.get("select count(*) from %s %s" % (table_name, where))['count(*)']
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
    rows = db.query("select * from %s %s "
                    "order by id desc limit %d,%d"
                    % (table_name, where, PER_PAGE_ROWS*(p-1), PER_PAGE_ROWS))

    return p, rows, pages


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
        userid = int(tornado.escape.xhtml_escape(self.current_user))
        p, rows, pages = get_page_rows(int(self.get_argument('p', 1)), 'vote_accounts', 'where admin_id=%d' % userid)

        self.render("static/admin/vote-accounts.html", rows=rows, pages=pages, p=p)


class SubAccountsHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        global db
        userid = int(tornado.escape.xhtml_escape(self.current_user))
        p, rows, pages = get_page_rows(int(self.get_argument('p', 1)), 'school_accounts', 'where admin_id=%d' % userid)

        for row in rows:
            v_row = db.get("select * from vote_accounts where app_id='%s'" % row.vote_account_id)
            row.vote_account_name = '%s (%s)' % (v_row['name'], v_row['display_id'])
        self.render("static/admin/sub-accounts.html", rows=rows, pages=pages, p=p)


class ClassesHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        global db
        userid = int(tornado.escape.xhtml_escape(self.current_user))
        sid = int(self.get_argument('sid', 1))
        sapp_id = ""

        schools = db.query("select * from school_accounts where admin_id=%d" % userid)
        finded = False
        for school in schools:
            if not sid == school.id:
                school.selected = False
            else:
                school.selected = True
                sapp_id = school.app_id
                finded = True

        if finded is False and len(schools) > 0:
            sid = schools[0].id
            sapp_id = schools[0].app_id

        p, rows, pages = get_page_rows(int(self.get_argument('p', 1)),
                                       'classes', 'where school_account_id="%s"' % sapp_id)

        self.render("static/admin/classes.html", schools=schools, sid=sid, rows=rows, pages=pages, p=p)


class PeopleHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        global db
        userid = int(tornado.escape.xhtml_escape(self.current_user))
        sid = int(self.get_argument('sid', 1))
        sapp_id = ""

        schools = db.query("select * from school_accounts where admin_id=%d" % userid)
        finded = False
        for school in schools:
            if not sid == school.id:
                school.selected = False
            else:
                school.selected = True
                sapp_id = school.app_id
                finded = True

        if finded is False and len(schools) > 0:
            sid = schools[0].id
            sapp_id = schools[0].app_id

        p, rows, pages = get_page_rows(int(self.get_argument('p', 1)),
                                       'voted_people', 'where school_account_id="%s"' % sapp_id)

        self.render("static/admin/people.html", schools=schools, sid=sid, rows=rows, pages=pages, p=p)


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


class LogoutHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("user")
        self.redirect('/login', permanent=True)


class ReloadCacheHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        refresh = int(self.get_argument('refresh', 0))

        if refresh == 1:
            pass    # TODO

        self.render("static/admin/reload-cache.html")


class EditHandler(BaseHandler):
    def __init__(self, _application, request, **kwargs):
        BaseHandler.__init__(self, _application, request)
        self.title_prefix = kwargs['title_prefix']

    def data_received(self, chunk):
        pass

    def get(self, table):
        global db
        _id = int(self.get_argument('id', 0))

        title = ""
        rows = []
        if table == 'vote_accounts':
            title = self.title_prefix + u'投票账号'

            if self.title_prefix == u"编辑":
                rlt = db.get("select * from vote_accounts where id='%d'" % _id)
                if rlt is None:
                    self.redirect('/%s' % table, permanent=True)
                    return

            rows.append(dict(id='display_id', name='公众号微信号',
                             str='<input type="text" class="input-xlarge" id="display_id" value="" />'))

            rows.append(dict(id='active', name='接受投票',
                             str='<input type="checkbox" id="active" value="1" checked />'))

            selections = """
<select id="role">
<option value="admin" selected>Admin</option>
<option value="mod">Moderator</option>
<option value="user">User</option>
</select>
"""
            rows.append(dict(id='role', name='测试', str=selections))

        elif table == 'sub_accounts':
            title = self.title_prefix + u'小号'
            rlt = db.get("select * from school_accounts where id='%d'" % _id)
            if rlt is None:
                self.redirect('/%s' % table, permanent=True)
                return

        elif table == 'classes':
            title = self.title_prefix + u'班级'
            rlt = db.get("select * from classes where id='%d'" % _id)
            if rlt is None:
                self.redirect('/%s' % table, permanent=True)
                return

        else:
            self.write("404: Page not found.")
            return

        self.render("static/admin/edit.html", title=title, rows=rows)

    def post(self, table):
        global db
        _id = int(self.get_argument('id', 0))

        if table == 'vote_accounts':
            rlt = db.get("select * from vote_accounts where id='%d'" % _id)

        elif table == 'sub_accounts':
            rlt = db.get("select * from school_accounts where id='%d'" % _id)

        elif table == 'classes':
            rlt = db.get("select * from classes where id='%d'" % _id)

        self.redirect('/%s' % table, permanent=True)


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
        (r"/logout", LogoutHandler),
        (r"/reload_cache", ReloadCacheHandler),

        (r"/vote_accounts", VoteAccountsHandler),
        (r"/sub_accounts", SubAccountsHandler),
        (r"/classes", ClassesHandler),
        (r"/people", PeopleHandler),

        (r"/(.*)/edit", EditHandler, dict(title_prefix=u'编辑')),
        (r"/(.*)/add", EditHandler, dict(title_prefix=u'添加')),
    ], **settings)

    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()

