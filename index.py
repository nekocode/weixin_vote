#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import tornado
from tornado.web import Application, RequestHandler
from vote_model import SchoolAccount, VoteAccount
from weixin_helper import xml2dict, WeixinRefreshATKWorker

__author__ = 'nekocode'

domain = 'http://weixin_vote.tunnel.mobi'

# 排行榜 http://vote.bbdfun.com/uc/top?wechatname=%E5%90%89%E7%8F%A0%E7%9F%A5%E9%81%93
# http://dushu.xiaomi.com/#1

sub_accounts = {
    'wxfcc58491aa0b07d6': SchoolAccount({
        'app_id': 'wxfcc58491aa0b07d6',
        'app_secret': 'd4624c36b6795d1d99dcf0547af5443d',
        'token': 'nekocode',
        'aes_key': "wRR2E0BcY1nrniIe1gf8Otx8DtDG6ibOAYNHZilzakv",
    }, 'wxfcc58491aa0b07d6')
}

vote_accounts = {
    'wxfcc58491aa0b07d6': VoteAccount({
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
            text = msg['Content']

            if type(weixin) == VoteAccount:
                if text.startwith('V'):
                    vote_rlt = weixin.vote(text)

                    if vote_rlt == 0:   # 投票成功
                        reply_msg = weixin.news_msg(user, our, [{
                            'title': '恭喜你为【' + 'xxxx' + '】投票成功!',
                            'description': '查看目前排行榜',
                            'pic_url': 'http://mmbiz.qpic.cn/mmbiz/Wuhx7MUWdrdbtK3wdngeLY5uiaglJm9wi'
                                       'bNgMzWB0WJS1HsOTomORJia3ibIJlJGCYFXzofdM6o4yXEXIUPic4oux0w/640'
                                       '?wx_fmt=jpeg&tp=webp&wxfrom=5',  # todo：内链模板
                            'url': 'http://www.baidu.com'
                        }, {
                            'title': '▶点击此处获取邀请码',
                            'url': domain + '/invite/' + appid  # todo: 外链
                        }, {
                            'title': '点击此处查看排行榜~',
                            'url': domain + '/rank/' + appid
                        }])

                    elif vote_rlt == -1:
                        reply_msg = weixin.text_msg(user, our, '你的投票码有误，请尝试重新获取')

                    elif vote_rlt == -2:
                        reply_msg = weixin.text_msg(user, our, '你已经在该校投过一次票了，'
                                                               '快获取邀请码让你的小伙伴们来帮你投票吧')

                elif text.startwith('Q'):
                    # todo：提供所在学校的链接
                    reply_msg = weixin.text_msg(user, our, '请将邀请码发给你的小伙伴，'
                                                           '并在举办你所在学校比赛的子公众号内使用邀请码投票')

                else:
                    reply_msg = 'success'

            elif type(weixin) == SchoolAccount:
                if text.startwith('V'):
                    reply_msg = weixin.news_msg(user, our, [{
                        'title': '为防止刷票，请到该公众号下投票',
                        'url': 'http://www.baidu.com'
                    }])

                elif text.startwith('C'):
                    reply_msg = weixin.news_msg(user, our, [{
                        'title': '你还差一步即可成功为【' + 'xxxx' + '】投票',
                        'description': '查看目前排行榜',
                        'pic_url': 'http://mmbiz.qpic.cn/mmbiz/Wuhx7MUWdrdbtK3wdngeLY5uiaglJm9wibN'
                                    'gMzWB0WJS1HsOTomORJia3ibIJlJGCYFXzofdM6o4yXEXIUPic4oux0w/640?wx_'
                                    'fmt=jpeg&tp=webp&wxfrom=5',  # todo：内链模板
                        'url': 'http://www.baidu.com'
                    }, {
                        'title': '▶点击此处完成投票操作',
                        'url': domain + '/vote/' + appid  # todo: 外链
                    }, {
                        'title': '点击此处查看排行榜~',
                        'url': domain + '/rank/' + appid
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



