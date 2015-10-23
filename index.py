#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
import os
import time
import tornado
import tornado.web
from weixin_helper import WeixinHelper, xml2dict, WeixinRefreshATKWorker

__author__ = 'nekocode'


app_id = 'wxfcc58491aa0b07d6'
app_secret = 'd4624c36b6795d1d99dcf0547af5443d'
token = 'nekocode'
aes_key = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG"
weixin = WeixinHelper(app_id, app_secret, token, aes_key)


class MainHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        signature = self.get_argument("signature")
        timestamp = self.get_argument("timestamp")
        nonce = self.get_argument("nonce")
        echostr = self.get_argument("echostr")

        if weixin.check_signature(signature, timestamp, nonce):
            self.write(echostr)
        else:
            self.write("failed")

    def post(self, *args, **kwargs):
        # todo: 设为安全模式，并解密消息
        msg = xml2dict(self.request.body)
        if msg['MsgType'] == 'text':
            # weixin.encrypt_msg()
            self.write("success")
        else:
            self.write("success")


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static")
}

application = tornado.web.Application([
    (r"/", MainHandler)
], **settings)


if __name__ == '__main__':
    # WeixinRefreshATKWorker(weixin).start()

    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()



