#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import tornado.web

from handler import admin, wx_backend, wx_frontend
from model.vote_model import school_accounts, vote_accounts


reload(sys)
sys.setdefaultencoding('utf-8')


url = [
    (r'/sub_account/(.*)', wx_backend.WXAccountMsgHandler, dict(accounts=school_accounts)),
    (r'/vote_account/(.*)', wx_backend.WXAccountMsgHandler, dict(accounts=vote_accounts)),
    (r'/vote_code/(.*)', wx_frontend.VoteCodeHandler),
    (r'/qrcode/(.*)', wx_frontend.QRCodeHandler),
    (r'/invite_code/(.*)', wx_frontend.InviteCodeHandler),
    (r'/rank/(.*)', wx_frontend.RankHandler),

    (r'/', tornado.web.RedirectHandler, {"url": "/login", "permanent": False}),
    (r"/login", admin.LoginHandler),
    (r"/logout", admin.LogoutHandler),
    (r"/reload_cache", admin.ReloadCacheHandler),

    (r"/vote_accounts", admin.VoteAccountsHandler),
    (r"/sub_accounts", admin.SubAccountsHandler),
    (r"/classes", admin.ClassesHandler),
    (r"/people", admin.PeopleHandler),

    (r"/(.*)/backend_url", admin.BackendUrlHandler),
    (r"/(.*)/edit", admin.EditHandler, dict(title_prefix=u'编辑')),
    (r"/(.*)/add", admin.EditHandler, dict(title_prefix=u'添加')),
    (r"/(.*)/delete", admin.DeleteAccountHandler),
    (r"/upload", admin.UploadHandler),
]

