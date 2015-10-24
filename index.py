#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import tornado
from tornado.web import Application, RequestHandler
from weixin_helper import WeixinHelper, xml2dict, WeixinRefreshATKWorker

__author__ = 'nekocode'

domain = 'http://weixin_vote.tunnel.mobi'

sub_accounts = {
    'wxfcc58491aa0b07d6': WeixinHelper({
        'app_id': 'wxfcc58491aa0b07d6',
        'app_secret': 'd4624c36b6795d1d99dcf0547af5443d',
        'token': 'nekocode',
        'aes_key': "wRR2E0BcY1nrniIe1gf8Otx8DtDG6ibOAYNHZilzakv",

        'vote_account_id': 'wxfcc58491aa0b07d6'
    })
}

vote_accounts = {
    'wxfcc58491aa0b07d6': WeixinHelper({
        'app_id': 'wxfcc58491aa0b07d6',
        'app_secret': 'd4624c36b6795d1d99dcf0547af5443d',
        'token': 'nekocode',
        'aes_key': "wRR2E0BcY1nrniIe1gf8Otx8DtDG6ibOAYNHZilzakv"
    })
}


class MainHandler(RequestHandler):
    def __init__(self, _application, request, **kwargs):
        RequestHandler.__init__(self, _application, request)
        self.accounts = kwargs['accounts']
        self.is_vote_account = kwargs['is_vote_account']

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

            elif msg['Content'] == 'C':     # 邀请的公众号
                reply_msg = weixin.news_msg(user, our, [{
                    'title': '你还差一步即可成功为【' + 'xxxx' + '】投票',
                    'description': '查看目前排行榜',
                    'pic_url': 'http://img5.imgtn.bdimg.com/it/u=1478080219,1136989624&fm=21&gp=0.jpg',  # todo：内链模板
                    'url': 'http://www.baidu.com'
                }, {
                    'title': '▶点击此处完成投票操作',
                    'url': domain + '/vote/' + appid  # todo: 外链
                }, {
                    'title': '点击此处查看排行榜~',
                    'url': domain + '/rank/' + appid
                }])

            elif msg['Content'] == 'V':
                reply_msg = weixin.news_msg(user, our, [{
                    'title': '恭喜你为【' + 'xxxx' + '】投票成功!',
                    'description': '查看目前排行榜',
                    'pic_url': 'http://img5.imgtn.bdimg.com/it/u=1478080219,1136989624&fm=21&gp=0.jpg',  # todo：内链模板
                    'url': 'http://www.baidu.com'
                }, {
                    'title': '▶点击此处获取邀请码',
                    'url': domain + '/invite/' + appid  # todo: 外链
                }, {
                    'title': '点击此处查看排行榜~',
                    'url': domain + '/rank/' + appid
                }])

            elif msg['Content'] == 'rank':
                reply_msg = weixin.news_msg(user, our, [{
                    'title': '排行榜',
                    'description': '查看目前排行榜',
                    'pic_url': 'http://img5.imgtn.bdimg.com/it/u=1478080219,1136989624&fm=21&gp=0.jpg',
                    'url': 'http://www.baidu.com'
                }, {
                    'title': '获取邀请码',
                    'url': 'http://www.baidu.com'
                }])

            else:
                reply_msg = 'success'

            self.write(reply_msg)

        else:
            self.write('success')


class VoteHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, app_id):
        self.write('为了防止刷票，你的验证码是 V12345')


class RankHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, app_id):
        self.write('排行榜：' + app_id)


class InviteHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, app_id):
        self.write('你的邀请码')

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static")
}

application = Application([
    (r'/sub_account/(.*)', MainHandler, dict(accounts=sub_accounts, is_vote_account=False)),
    (r'/vote_account/(.*)', MainHandler, dict(accounts=vote_accounts, is_vote_account=True)),
    (r'/vote/(.*)', VoteHandler),
    (r'/rank/(.*)', RankHandler),
    (r'/invite/(.*)', InviteHandler)
], **settings)


if __name__ == '__main__':
    # for key, invite_weixin in invite_account.items():
    #     WeixinRefreshATKWorker(invite_weixin).start()
    #
    # for key, vote_weixin in vote_account.items():
    #     WeixinRefreshATKWorker(vote_weixin).start()

    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()



