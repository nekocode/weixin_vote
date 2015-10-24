#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import tornado
import tornado.web
from weixin_helper import WeixinHelper, xml2dict, WeixinRefreshATKWorker

__author__ = 'nekocode'

invite_account = {
    'wxfcc58491aa0b07d6': WeixinHelper({
        'app_id': 'wxfcc58491aa0b07d6',
        'app_secret': 'd4624c36b6795d1d99dcf0547af5443d',
        'token': 'nekocode',
        'aes_key': "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG",

        'vote_account_app_id': None
    })
}

vote_account = {
    'wxfcc58491aa0b07d6': WeixinHelper({
        'app_id': 'wxfcc58491aa0b07d6',
        'app_secret': 'd4624c36b6795d1d99dcf0547af5443d',
        'token': 'nekocode',
        'aes_key': "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG",

        'invite_account_app_id': None
    })
}


class InviteHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, appid):
        if appid not in invite_account:
            self.write('failed')
            return
        weixin = invite_account[appid]

        signature = self.get_argument("signature")
        timestamp = self.get_argument("timestamp")
        nonce = self.get_argument("nonce")
        echostr = self.get_argument("echostr")

        if weixin.check_signature(signature, timestamp, nonce):
            self.write(echostr)
        else:
            self.write("failed")

    def post(self, appid):
        if appid not in invite_account:
            self.write('failed')
            return
        weixin = invite_account[appid]

        # todo: 设为安全模式，并解密消息
        msg = xml2dict(self.request.body)
        if msg['MsgType'] == 'text':
            # weixin.encrypt_msg()
            self.write("success")
        else:
            self.write("success")


class VoteHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, appid):
        if appid not in vote_account:
            self.write('failed')
            return
        weixin = vote_account[appid]

        signature = self.get_argument("signature")
        timestamp = self.get_argument("timestamp")
        nonce = self.get_argument("nonce")
        echostr = self.get_argument("echostr")

        if weixin.check_signature(signature, timestamp, nonce):
            self.write(echostr)
        else:
            self.write("failed")

    def post(self, appid):
        if appid not in vote_account:
            self.write('failed')
            return
        weixin = vote_account[appid]

        # todo: 设为安全模式，并解密消息
        msg = xml2dict(self.request.body)
        if msg['MsgType'] == 'text':
            # weixin.encrypt_msg()
            self.write("success")
        else:
            self.write("success")


class NewsHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static")
}

application = tornado.web.Application([
    (r'/invite/(.*)', InviteHandler),
    (r'/vote/(.*)', VoteHandler),
    (r'/news', NewsHandler)
], **settings)


if __name__ == '__main__':
    # for key, invite_weixin in invite_account.items():
    #     WeixinRefreshATKWorker(invite_weixin).start()
    #
    # for key, vote_weixin in vote_account.items():
    #     WeixinRefreshATKWorker(vote_weixin).start()

    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()



