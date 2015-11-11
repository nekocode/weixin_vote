#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import config
import torndb
import tornado
from tornado.web import Application, RequestHandler, os
import vote_model
from weixin_sougou import get_account_info

PER_PAGE_ROWS = 20


def get_page_rows(p, table_name, where=''):
    # 获取分页数量
    row_count = vote_model.db.get("select count(*) from %s %s" % (table_name, where))['count(*)']
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
    rows = vote_model.db.query("select * from %s %s order by id desc limit %d,%d"
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
        userid = int(tornado.escape.xhtml_escape(self.current_user))
        p, rows, pages = get_page_rows(int(self.get_argument('p', 1)), 'school_accounts', 'where admin_id=%d' % userid)

        for row in rows:
            v_row = vote_model.db.get("select * from vote_accounts where app_id='%s'" % row.vote_account_id)
            row.vote_account_name = '%s (%s)' % (v_row['name'], v_row['display_id'])
        self.render("static/admin/sub-accounts.html", rows=rows, pages=pages, p=p)


class ClassesHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        userid = int(tornado.escape.xhtml_escape(self.current_user))
        sid = int(self.get_argument('sid', 1))
        sapp_id = ""

        schools = vote_model.db.query("select * from school_accounts where admin_id=%d" % userid)
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
        userid = int(tornado.escape.xhtml_escape(self.current_user))
        sid = int(self.get_argument('sid', 1))
        sapp_id = ""

        schools = vote_model.db.query("select * from school_accounts where admin_id=%d" % userid)
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

        rlt = vote_model.db.get("select * from users where username='%s' and password='%s'" % (name, pwd))

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
            vote_model.cahe_accounts()
            self.write("部署成功")
        else:
            self.render("static/admin/reload-cache.html")


class EditHandler(BaseHandler):
    def __init__(self, _application, request, **kwargs):
        BaseHandler.__init__(self, _application, request)
        self.title_prefix = kwargs['title_prefix']

    def data_received(self, chunk):
        pass

    @tornado.web.authenticated
    def get(self, table):
        userid = int(tornado.escape.xhtml_escape(self.current_user))
        _id = int(self.get_argument('id', 0))

        sidebar_select = 0
        title = ""
        rows = []
        if table == 'vote_accounts':
            sidebar_select = 0
            title = self.title_prefix + u'投票账号'

            rlt = None
            if self.title_prefix == u"编辑":
                rlt = vote_model.db.get("select * from vote_accounts where id=%d" % _id)
                if rlt is None:
                    self.redirect('/%s' % table, permanent=True)
                    return

            rows.append(dict(name='公众号微信号',
                             str='<input type="text" class="input-xlarge" name="display_id" value="%s" />'
                                 % (rlt.display_id if rlt is not None else "")))

            rows.append(dict(name='app_id',
                             str='<input type="text" class="input-xlarge" name="app_id" value="%s" />'
                                 % (rlt.app_id if rlt is not None else "")))

            rows.append(dict(name='app_secret',
                             str='<input type="text" class="input-xlarge" name="app_secret" value="%s" />'
                                 % (rlt.app_secret if rlt is not None else "")))

            rows.append(dict(name='token',
                             str='<input type="text" class="input-xlarge" name="token" value="%s" />'
                                 % (rlt.token if rlt is not None else "")))

            rows.append(dict(name='接受投票',
                             str='<input type="checkbox" name="active" value=1 %s />'
                                 % ("checked" if rlt is None or rlt.active == 1 else "")))

        elif table == 'sub_accounts':
            sidebar_select = 1
            title = self.title_prefix + u'小号'

            rlt = None
            if self.title_prefix == u"编辑":
                rlt = vote_model.db.get("select * from school_accounts where id=%d" % _id)
                if rlt is None:
                    self.redirect('/%s' % table, permanent=True)
                    return

            rows.append(dict(name='公众号微信号',
                             str='<input type="text" class="input-xlarge" name="display_id" value="%s" />'
                                 % (rlt.display_id if rlt is not None else "")))

            rows.append(dict(name='app_id',
                             str='<input type="text" class="input-xlarge" name="app_id" value="%s" />'
                                 % (rlt.app_id if rlt is not None else "")))

            rows.append(dict(name='app_secret',
                             str='<input type="text" class="input-xlarge" name="app_secret" value="%s" />'
                                 % (rlt.app_secret if rlt is not None else "")))

            rows.append(dict(name='token',
                             str='<input type="text" class="input-xlarge" name="token" value="%s" />'
                                 % (rlt.token if rlt is not None else "")))

            rows.append(dict(name='学校名字',
                             str='<input type="text" class="input-xlarge" name="school_name" value="%s" />'
                                 % (rlt.school_name if rlt is not None else "")))

            rows.append(dict(name='介绍页面 URL',
                             str='<input type="text" class="input-xlarge" name="intro_url" value="%s" />'
                                 % (rlt.intro_url if rlt is not None else "")))

            rows.append(dict(name='介绍页面背景图 URL',
                             str='<input type="text" class="input-xlarge" name="intro_img_url" value="%s" />'
                                 % (rlt.intro_img_url if rlt is not None else "")))

            vote_accounts = vote_model.db.query("select * from vote_accounts where admin_id=%d" % userid)
            selections = '<select name="vote_account_id">'
            for vote_account in vote_accounts:
                selections += '<option value="%s">%s(%s)</option>' \
                              % (vote_account.app_id,
                                 tornado.escape.xhtml_escape(vote_account.name),
                                 vote_account.display_id)
            selections += '</select>'

            rows.append(dict(name='对应投票公众号', str=selections))

            rows.append(dict(name='接受投票',
                             str='<input type="checkbox" name="active" value=1 %s />'
                                 % ("checked" if rlt is None or rlt.active == 1 else "")))

        elif table == 'classes':
            sidebar_select = 2
            title = self.title_prefix + u'班级'

            sid = int(self.get_argument("sid", 0))
            rlt = vote_model.db.get("select * from school_accounts where id=%d" % sid)
            if rlt is None:
                self.redirect('/%s' % table, permanent=True)
                return

            rlt = None
            if self.title_prefix == u"编辑":
                rlt = vote_model.db.get("select * from classes where id=%d" % _id)
                if rlt is None:
                    self.redirect('/%s' % table, permanent=True)
                    return

            rows.append(dict(name='班级名称',
                             str='<input type="text" class="input-xlarge" name="class_name" value="%s" />'
                                 % (rlt.class_name if rlt is not None else "")))

            rows.append(dict(name='班级图片 URL',
                             str='<input type="text" class="input-xlarge" name="pic_url" value="%s" />'
                                 % (rlt.pic_url if rlt is not None else "")))

        else:
            self.write("404: Page not found.")
            return

        self.render("static/admin/edit.html",sidebar_select=sidebar_select, title=title, rows=rows)

    @tornado.web.authenticated
    def post(self, table):
        userid = int(tornado.escape.xhtml_escape(self.current_user))
        _id = int(self.get_argument('id', 0))

        if table == 'vote_accounts':
            user = vote_model.db.get("select * from users where id=%d" % userid)
            if user is None or user.access_vote == 0:
                self.write(u"你没有权限进行该操作")
                return

            display_id = self.get_body_argument('display_id')
            app_id = MySQLdb.escape_string(self.get_body_argument('app_id'))
            rlt = vote_model.db.get("select * from vote_accounts where id=%d" % _id)

            if rlt is None:
                exist = vote_model.db.get("select * from vote_accounts where app_id='%s'" % app_id)
                if exist is not None:
                    self.write(u"该 app_id 已被登记，请使用其他公众号")
                    return
                exist = vote_model.db.get("select * from school_accounts where app_id='%s'" % app_id)
                if exist is not None:
                    self.write(u"该 app_id 已被登记，请使用其他公众号")
                    return

                account_info = get_account_info(display_id)

                if account_info is None:
                    self.write(u"找不到该公众号")
                    return

                # 添加
                sql = "insert into vote_accounts(" \
                      "app_id, app_secret, token, aes_key, admin_id, name, display_id, avatar_url, qrcode_url, active) " \
                      "values('%s', '%s', '%s', '%s', %d, '%s', '%s', '%s', '%s', %s)" \
                      % (app_id,
                         MySQLdb.escape_string(self.get_body_argument('app_secret')),
                         MySQLdb.escape_string(self.get_body_argument('token')),
                         "", userid,
                         MySQLdb.escape_string(account_info['name'].encode('utf8')),
                         MySQLdb.escape_string(display_id),
                         MySQLdb.escape_string(account_info['logo']),
                         MySQLdb.escape_string(account_info['qr_code']),
                         "false" if self.get_body_argument('active', None) is None else "true")
                try:
                    vote_model.db.insert(sql)
                    self.redirect('/%s' % table, permanent=True)
                except Exception, e:
                    print Exception, ":", e
                    self.write(u'操作失败，请确认你填写的数据无误')

            else:
                # 编辑
                if not rlt.display_id == display_id:
                    # 公众号改变，重新获取账户信息
                    account_info = get_account_info(display_id)
                else:
                    account_info = dict(name=rlt.name, logo=rlt.avatar_url, qr_code=rlt.qrcode_url)

                sql = "update vote_accounts set app_id='%s', app_secret='%s', token='%s', name='%s', " \
                      "display_id='%s', avatar_url='%s', qrcode_url = '%s', active = %s where id=%d" \
                      % (MySQLdb.escape_string(self.get_body_argument('app_id')),
                         MySQLdb.escape_string(self.get_body_argument('app_secret')),
                         MySQLdb.escape_string(self.get_body_argument('token')),
                         MySQLdb.escape_string(account_info['name'].encode('utf8')),
                         MySQLdb.escape_string(display_id),
                         MySQLdb.escape_string(account_info['logo']),
                         MySQLdb.escape_string(account_info['qr_code']),
                         "false" if self.get_body_argument('active', None) is None else "true",
                         _id)

                try:
                    vote_model.db.update(sql)
                    self.redirect('/%s' % table, permanent=True)
                except Exception, e:
                    print Exception, ":", e
                    self.write(u'操作失败，请确认你填写的数据无误')

        elif table == 'sub_accounts':
            display_id = self.get_body_argument('display_id')
            app_id = MySQLdb.escape_string(self.get_body_argument('app_id'))
            rlt = vote_model.db.get("select * from school_accounts where id=%d" % _id)

            if rlt is None:
                # 添加

                exist = vote_model.db.get("select * from vote_accounts where app_id='%s'" % app_id)
                if exist is not None:
                    self.write(u"该 app_id 已被登记，请使用其他公众号")
                    return
                exist = vote_model.db.get("select * from school_accounts where app_id='%s'" % app_id)
                if exist is not None:
                    self.write(u"该 app_id 已被登记，请使用其他公众号")
                    return

                account_info = get_account_info(display_id)

                if account_info is None:
                    self.write(u"找不到该公众号")
                    return

                sql = "insert into school_accounts(" \
                      "app_id, app_secret, token, aes_key, admin_id, name, display_id, avatar_url, qrcode_url, active, " \
                      "school_name, voting_count, intro_url, intro_img_url, vote_account_id) " \
                      "values('%s', '%s', '%s', '%s', %d, '%s', '%s', '%s', '%s', %s, " \
                      "'%s', %d, '%s', '%s', '%s')" \
                      % (MySQLdb.escape_string(self.get_body_argument('app_id')),
                         MySQLdb.escape_string(self.get_body_argument('app_secret')),
                         MySQLdb.escape_string(self.get_body_argument('token')),
                         "", userid,
                         MySQLdb.escape_string(account_info['name'].encode('utf8')),
                         MySQLdb.escape_string(display_id),
                         MySQLdb.escape_string(account_info['logo']),
                         MySQLdb.escape_string(account_info['qr_code']),
                         "false" if self.get_body_argument('active', None) is None else "true",
                         MySQLdb.escape_string(self.get_body_argument('school_name').encode('utf8')),
                         0,
                         MySQLdb.escape_string(self.get_body_argument('intro_url')),
                         MySQLdb.escape_string(self.get_body_argument('intro_img_url')),
                         MySQLdb.escape_string(self.get_body_argument('vote_account_id')))
                try:
                    vote_model.db.insert(sql)
                    self.redirect('/%s' % table, permanent=True)
                except Exception, e:
                    print Exception, ":", e
                    self.write(u'操作失败，请确认你填写的数据无误')

            else:
                # 编辑
                if not rlt.display_id == display_id:
                    # 公众号改变，重新获取账户信息
                    account_info = get_account_info(display_id)
                else:
                    account_info = dict(name=rlt.name, logo=rlt.avatar_url, qr_code=rlt.qrcode_url)

                sql = "update school_accounts set app_id='%s', app_secret='%s', token='%s', name='%s', " \
                      "display_id='%s', avatar_url='%s', qrcode_url='%s', active=%s ," \
                      "school_name='%s', intro_url='%s', intro_img_url='%s', vote_account_id='%s' where id=%d" \
                      % (MySQLdb.escape_string(self.get_body_argument('app_id')),
                         MySQLdb.escape_string(self.get_body_argument('app_secret')),
                         MySQLdb.escape_string(self.get_body_argument('token')),
                         MySQLdb.escape_string(account_info['name'].encode('utf8')),
                         MySQLdb.escape_string(display_id),
                         MySQLdb.escape_string(account_info['logo']),
                         MySQLdb.escape_string(account_info['qr_code']),
                         "false" if self.get_body_argument('active', None) is None else "true",
                         MySQLdb.escape_string(self.get_body_argument('school_name').encode('utf8')),
                         MySQLdb.escape_string(self.get_body_argument('intro_url')),
                         MySQLdb.escape_string(self.get_body_argument('intro_img_url')),
                         MySQLdb.escape_string(self.get_body_argument('vote_account_id')),
                         _id)

                try:
                    vote_model.db.update(sql)
                    self.redirect('/%s' % table, permanent=True)
                except Exception, e:
                    print Exception, ":", e
                    self.write(u'操作失败，请确认你填写的数据无误')

        elif table == 'classes':
            sid = int(self.get_argument("sid", 0))
            school_account = vote_model.db.get("select * from school_accounts where id=%d" % sid)
            if school_account is None:
                self.redirect('/%s' % table, permanent=True)
                return

            rlt = vote_model.db.get("select * from classes where id=%d" % _id)

            if rlt is None:
                # 添加
                sql = "insert into classes(class_name, voting_count, pic_url, school_account_id) " \
                      "values('%s', %d, '%s', '%s')" \
                      % (MySQLdb.escape_string(self.get_body_argument('class_name').encode('utf8')),
                         0,
                         MySQLdb.escape_string(self.get_body_argument('pic_url')),
                         school_account.app_id.encode('utf8'))

                try:
                    vote_model.db.insert(sql)
                    self.redirect('/%s' % table, permanent=True)

                except Exception, e:
                    print Exception, ":", e
                    self.write(u'操作失败，请确认你填写的数据无误')

            else:
                # 编辑
                sql = "update classes set class_name='%s' where id=%d" % (
                    MySQLdb.escape_string(self.get_body_argument('class_name').encode('utf8')),
                    _id)

                try:
                    vote_model.db.update(sql)
                    self.redirect('/%s' % table, permanent=True)
                except Exception, e:
                    print Exception, ":", e
                    self.write(u'操作失败，请确认你填写的数据无误')


class BackendUrlHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    def get(self, account_type):
        _id = int(self.get_argument('id', 0))

        if account_type == 'vote_accounts':
            rlt = vote_model.db.get('select * from vote_accounts where id=%d' % _id)
            self.write('您的公众号后台配置地址为： ' + config.DOMAIN + '/vote_account/' + rlt.app_id)

        elif account_type == 'sub_accounts':
            rlt = vote_model.db.get('select * from school_accounts where id=%d' % _id)
            self.write('您的公众号后台配置地址为： ' + config.DOMAIN + '/sub_account/' + rlt.app_id)

        else:
            self.write('不存在该 id')


class DeleteAccountHandler(BaseHandler):
    def data_received(self, chunk):
        pass

    def get(self, account_type):
        userid = int(tornado.escape.xhtml_escape(self.current_user))
        _id = int(self.get_argument('id', 0))

        if account_type == 'vote_accounts':
            user = vote_model.db.get("select * from users where id=%d" % userid)
            if user is None or user.access_vote == 0:
                self.write(u"你没有权限进行该操作")
                return

            rlt = vote_model.db.delete('delete from vote_accounts where id=%d' % _id)
            self.redirect('/%s' % account_type, permanent=True)

        elif account_type == 'sub_accounts':
            rlt = vote_model.db.delete('delete from school_accounts where id=%d' % _id)
            self.redirect('/%s' % account_type, permanent=True)

        elif account_type == 'classes':
            rlt = vote_model.db.delete('delete from classes where id=%d' % _id)
            self.redirect('/%s' % account_type, permanent=True)

        else:
            self.write('路径错误')

if __name__ == '__main__':
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

        (r"/(.*)/backend_url", BackendUrlHandler),
        (r"/(.*)/edit", EditHandler, dict(title_prefix=u'编辑')),
        (r"/(.*)/add", EditHandler, dict(title_prefix=u'添加')),
        (r"/(.*)/delete", DeleteAccountHandler),
    ], **settings)

    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()

