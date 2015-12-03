#!/usr/bin/python
# -*- coding: utf-8 -*-
from tornado.web import RequestHandler

import config
from wx_util.weixin_helper import xml2dict
from model.vote_model import SchoolAccount, VoteAccount, school_accounts


class WXAccountMsgHandler(RequestHandler):
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

            reply_msg = account.text_msg(user, our, '感谢你的留言，工作人员会尽快回复你。')

            if isinstance(account, VoteAccount):
                if account.active is False:
                    self.write(account.text_msg(user, our, '本账号已关闭投票'))
                    return

                if text.startswith('V'):
                    user_info = account.get_user_info(user)
                    # if user_info is None:
                    #     self.write(account.text_msg(user, our, 'AccseeToken 失效.'))
                    #     return

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
                                'url': config.DOMAIN + '/invite_code/' + invite_code
                            }, {
                                'title': '点击此处查看排行榜~',
                                'url': config.DOMAIN + '/rank/' + school_account_app_id
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
                        'url': config.DOMAIN + '/qrcode/' + account.vote_account_id
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
                            'url': config.DOMAIN + '/vote_code/' + account.vote_account_id + '?vc=' + vote_code
                        }, {
                            'title': '点击此处查看排行榜~',
                            'url': config.DOMAIN + '/rank/' + appid
                        }])

        self.write(reply_msg)


