#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import tornado
import tornado.web
from tornado.template import Template
from weixin_helper import WeixinHelper, xml2dict, WeixinRefreshATKWorker

__author__ = 'nekocode'

invite_account = {
    'wxfcc58491aa0b07d6': WeixinHelper({
        'app_id': 'wxfcc58491aa0b07d6',
        'app_secret': 'd4624c36b6795d1d99dcf0547af5443d',
        'token': 'nekocode',
        'aes_key': "wRR2E0BcY1nrniIe1gf8Otx8DtDG6ibOAYNHZilzakv",

        'vote_account_app_id': None
    })
}

vote_account = {
    'wxfcc58491aa0b07d6': WeixinHelper({
        'app_id': 'wxfcc58491aa0b07d6',
        'app_secret': 'd4624c36b6795d1d99dcf0547af5443d',
        'token': 'nekocode',
        'aes_key': "wRR2E0BcY1nrniIe1gf8Otx8DtDG6ibOAYNHZilzakv",

        'invite_account_app_id': None
    })
}


class WeixinHandler(tornado.web.RequestHandler):
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

        # msg = xml2dict(weixin.decrypt_xml(self.request.body))  todo: 解密
        msg = xml2dict(self.request.body)
        print msg
        if msg['MsgType'] == 'text':
            from_user = msg['FromUserName']
            to_user = msg['ToUserName']

            if msg['Content'] == 'h':
                reply_msg = weixin.text_msg(from_user, to_user, '哈哈哈哈')

            else:
                reply_msg = weixin.news_msg(from_user, to_user, [{
                    'title': '哈哈哈哈',
                    'description': '这是一个悲伤的消息',
                    'pic_url': 'http://img5.imgtn.bdimg.com/it/u=1478080219,1136989624&fm=21&gp=0.jpg',
                    'url': 'http://www.baidu.com'
                }, {
                    'title': '哈哈哈哈',
                    'url': 'http://www.baidu.com',
                    'description': '然而并日了狗',
                }])
            print reply_msg
            self.write(reply_msg)
            
        else:
            self.write('success')


class InviteHandler(WeixinHandler):
    def data_received(self, chunk):
        pass

    def get(self, appid):
        WeixinHandler.get(self, appid)

    def post(self, appid):
        WeixinHandler.post(self, appid)


class VoteHandler(WeixinHandler):
    def data_received(self, chunk):
        pass

    def get(self, appid):
        WeixinHandler.get(self, appid)

    def post(self, appid):
        WeixinHandler.post(self, appid)


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



