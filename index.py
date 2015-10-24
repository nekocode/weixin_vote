#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import tornado
from tornado.web import Application, RequestHandler
from tornado.template import Template
from weixin_helper import WeixinHelper, xml2dict, WeixinRefreshATKWorker

__author__ = 'nekocode'

invite_accounts = {
}

vote_accounts = {
    'wxfcc58491aa0b07d6': WeixinHelper({
        'app_id': 'wxfcc58491aa0b07d6',
        'app_secret': 'd4624c36b6795d1d99dcf0547af5443d',
        'token': 'nekocode',
        'aes_key': "wRR2E0BcY1nrniIe1gf8Otx8DtDG6ibOAYNHZilzakv",

        'invite_account_app_id': None
    })
}


class WeixinHandler(RequestHandler):
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
        weixin = self.accounts[appid]

        # msg = xml2dict(weixin.decrypt_xml(self.request.body))  todo: 解密
        msg = xml2dict(self.request.body)
        print msg
        if msg['MsgType'] == 'text':
            user = msg['FromUserName']
            our = msg['ToUserName']

            if msg['Content'] == 'h':
                reply_msg = weixin.text_msg(user, our, 'hahah')

            else:
                reply_msg = weixin.news_msg(user, our, [{
                    'title': '哈哈哈哈',
                    'description': '这是一个悲伤的消息',
                    'pic_url': 'http://img5.imgtn.bdimg.com/it/u=1478080219,1136989624&fm=21&gp=0.jpg',
                    'url': 'http://www.baidu.com'
                }, {
                    'title': '哈哈哈哈',
                    'url': 'http://www.baidu.com'
                }])
            print reply_msg
            self.write(reply_msg)

        else:
            self.write('success')


class ArticleHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, article_id):
        pass


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static")
}

application = Application([
    (r'/invite/(.*)', WeixinHandler, dict(accounts=invite_accounts)),
    (r'/vote/(.*)', WeixinHandler, dict(accounts=vote_accounts)),
    (r'/article/(.*)', ArticleHandler)
], **settings)


if __name__ == '__main__':
    # for key, invite_weixin in invite_account.items():
    #     WeixinRefreshATKWorker(invite_weixin).start()
    #
    # for key, vote_weixin in vote_account.items():
    #     WeixinRefreshATKWorker(vote_weixin).start()

    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()



