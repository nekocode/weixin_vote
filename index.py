#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import tornado
from tornado.web import Application, RequestHandler
import admin
from vote_model import SchoolAccount, VoteAccount, school_accounts, vote_accounts, init_db, cahe_accounts
from weixin_helper import xml2dict, WeixinRefreshATKWorker
import config

__author__ = 'nekocode'

domain = config.DOMAIN


reload(sys)
sys.setdefaultencoding('utf-8')


class MainHandler(RequestHandler):
    def __init__(self, _application, request, **kwargs):
        RequestHandler.__init__(self, _application, request)
        self.accounts = kwargs['accounts']

    def data_received(self, chunk):
        pass

    def get(self, appid):
        if appid not in self.accounts:
            self.write('failed')
            return
        weixin = self.accounts[appid]

        signature = self.get_argument("signature")
        timestamp = self.get_argument("timestamp")
        nonce = self.get_argument("nonce")
        echostr = self.get_argument("echostr")

        if weixin.check_signature(signature, timestamp, nonce):
            self.write(echostr)
        else:
            self.write("failed")

    def post(self, appid):
        if appid not in self.accounts:
            self.write('failed')
            return
        account = self.accounts[appid]

        # msg = xml2dict(weixin.decrypt_xml(self.request.body))  todo: 解密
        msg = xml2dict(self.request.body)
        print msg

        reply_msg = 'success'
        if msg['MsgType'] == 'text':
            user = msg['FromUserName']
            our = msg['ToUserName']
            text = msg['Content'].upper()

            if isinstance(account, VoteAccount):
                if account.active is False:
                    self.write(account.text_msg(user, our, '本账号已关闭投票'))
                    return

                if text.startswith('V'):
                    user_info = account.get_user_info(user)
                    if user_info is None:
                        self.write(account.text_msg(user, our, 'AccseeToken 失效.'))
                        return

                    try:
                        vote_code = int(text[1:])
                        vote_rlt = account.vote(vote_code, user, user_info)
                        if type(vote_rlt) is tuple:  # 投票成功
                            invite_code = str(vote_rlt[0])
                            class_name = vote_rlt[1]
                            school_account_app_id = account.get_school_account_app_id(vote_code)
                            school_account = school_accounts[school_account_app_id]

                            reply_msg = account.news_msg(user, our, [{
                                'title': '恭喜你为【' + class_name + '】投票成功!',
                                'pic_url': school_account.intro_img_url,
                                'url': school_account.intro_url
                            }, {
                                'title': '▶点击此处获取邀请码',
                                'url': domain + '/invite_code/' + invite_code
                            }, {
                                'title': '点击此处查看排行榜~',
                                'url': domain + '/rank/' + school_account_app_id
                            }])

                        elif vote_rlt == -1:
                            reply_msg = account.text_msg(user, our, '你的投票码有误，请尝试重新获取')

                        elif vote_rlt == -2:
                            reply_msg = account.text_msg(user, our, '该投票码已经被使用过了，请尝试重新获取')

                        elif vote_rlt == -3:
                            # 贴出邀请码
                            reply_msg = account.text_msg(user, our, '你已经为该班级投过票了，每人只能为一个班级投一票')

                    except ValueError:
                        reply_msg = account.text_msg(user, our, '你的投票码有误，请尝试重新获取')

                elif text.startswith('I'):
                    # todo：提供所在学校的公众号 qrcode
                    reply_msg = account.text_msg(user, our, '请将邀请码发给你的小伙伴，'
                                                            '并在举办你所在学校比赛的子公众号内使用邀请码投票')

            elif isinstance(account, SchoolAccount):
                if account.active is False:
                    self.write(account.text_msg(user, our, '本账号已关闭投票'))
                    return

                if text.startswith('V'):
                    reply_msg = account.news_msg(user, our, [{
                        'title': '为防止刷票，请到该公众号下投票',
                        'url': domain + '/qrcode/' + account.vote_account_id
                    }])

                elif text.startswith('C') or text.startswith('I'):
                    rlt = account.get_vote_code(text)

                    if rlt is None:
                        if text.startswith('C'):
                            reply_msg = account.text_msg(user, our, '你的班级码有误')
                        elif text.startswith('I'):
                            reply_msg = account.text_msg(user, our, '你的邀请码有误')

                    else:
                        vote_code = str(rlt[0])
                        class_name = rlt[1]

                        reply_msg = account.news_msg(user, our, [{
                            'title': '你还差一步即可成功为【' + class_name + '】投票',
                            'pic_url': account.intro_img_url,
                            'url': account.intro_url
                        }, {
                            'title': '▶点击此处完成投票操作',
                            'url': domain + '/vote_code/' + account.vote_account_id + '?vc=' + vote_code
                        }, {
                            'title': '点击此处查看排行榜~',
                            'url': domain + '/rank/' + appid
                        }])

        self.write(reply_msg)


class VoteCodeHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, app_id):
        if app_id not in vote_accounts:
            self.write('打开姿势有误 ╮(╯_╰)╭')
            return
        account = vote_accounts[app_id]

        vote_code = 'V%05d' % int(self.get_argument('vc'))
        qrcode_url = account.qrcode_url
        account_name = account.name
        account_id = account.display_id

        self.render("static/vote/vote_code.html", vote_code=vote_code, qrcode_url=qrcode_url,
                    account_name=account_name, account_id=account_id)


class QRCodeHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, app_id):
        account = None
        if app_id in vote_accounts:
            account = vote_accounts[app_id]
        elif app_id in school_accounts:
            account = school_accounts[app_id]
        else:
            self.write('打开姿势有误 ╮(╯_╰)╭')
            return

        qrcode_url = account.qrcode_url
        account_name = account.name
        account_id = account.display_id

        self.render("static/vote/qrcode.html", qrcode_url=qrcode_url,
                    account_name=account_name, account_id=account_id)


class InviteCodeHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, invite_code):
        invite_code = 'I%05d' % int(invite_code)

        self.render("static/vote/invite_code.html", invite_code=invite_code)


class RankHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, app_id):
        if app_id not in school_accounts:
            self.write('打开姿势有误 ╮(╯_╰)╭')
            return
        account = school_accounts[app_id]
        class_rank_rows = account.get_classes_rank()
        person_rank_rows = account.get_person_rank()

        avatar_url = account.avatar_url
        qrcode_url = domain + '/qrcode/' + account.app_id
        school_name = account.school_name
        class_count = len(class_rank_rows)
        vote_total_count = account.voting_count

        self.render("static/vote/ranking.html",
                    class_rank_rows=class_rank_rows, person_rank_rows=person_rank_rows,
                    avatar_url=avatar_url, qrcode_url=qrcode_url, school_name=school_name, class_count=class_count,
                    vote_total_count=vote_total_count)


import uimodules
settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "61oETzKXQAGaYdk12345GeJJFuYh7EQnp2XdTP1o/Vo=",
    "login_url": "/login",
    "ui_modules": uimodules,
}

application = Application([
    (r'/sub_account/(.*)', MainHandler, dict(accounts=school_accounts)),
    (r'/vote_account/(.*)', MainHandler, dict(accounts=vote_accounts)),
    (r'/vote_code/(.*)', VoteCodeHandler),
    (r'/qrcode/(.*)', QRCodeHandler),
    (r'/invite_code/(.*)', InviteCodeHandler),
    (r'/rank/(.*)', RankHandler),

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
], **settings)


def server():
    init_db()           # 初始化数据库
    cahe_accounts()     # 缓存账户数据到内存

    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    server()

