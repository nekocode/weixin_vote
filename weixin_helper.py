#!/usr/bin/python
# -*- coding: utf-8 -*-

import hashlib
import json
import random
import string
import threading
import time
import httplib2
from xml.etree import cElementTree
# from weixin_crypt.WXBizMsgCrypt import WXBizMsgCrypt

__author__ = 'nekocode'


def xml2dict(xml):
    # 将 xml 转为 dict
    return dict((child.tag, child.text) for child in cElementTree.fromstring(xml))


def nonce_str(length=10):
    # 随机数
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def _cdata(data):
    # http://stackoverflow.com/questions/174890/how-to-output-cdata-using-elementtree
    return '<![CDATA[%s]]>' % data.replace(']]>', ']]]]><![CDATA[>')


class WeixinHelper:
    def __init__(self, account):
        if not ('app_id' in account and 'app_secret' in account and 'token' in account and 'aes_key' in account):
            raise AccountPropertyNotDefineException

        self.account = account
        self.app_id = account['app_id']
        self.app_secret = account['app_secret']
        self.token = account['token']
        self.aes_key = account['aes_key']

        self.access_token = None
        self.expires_in = 0     # 凭证有效时间，单位：秒

        self.http = httplib2.Http(timeout=5)

    def check_signature(self, signature, timestamp, nonce):
        # 验证微信对接签名
        array = [self.token, timestamp, nonce]
        array.sort()
        code = hashlib.sha1("".join(array)).hexdigest()
        return code == signature

    def refresh_access_token(self):
        # 刷新 access_token
        refresh_token_url = 'https://api.weixin.qq.com/cgi-bin/token?' \
                            'grant_type=client_credential&appid={0}&secret={1}' \
                            .format(self.app_id, self.app_secret)
        response, content = self.http.request(refresh_token_url, method="GET")
        rlt = json.loads(content)

        if 'errcode' in rlt:
            self.deal_err(rlt)
            return False
        else:
            self.access_token = rlt['access_token']
            self.expires_in = rlt['expires_in']
            return True

    def get_user_info(self, open_id, lang='zh_CN'):
        user_info_url = 'https://api.weixin.qq.com/cgi-bin/user/info?' \
                        'access_token={0}&openid={1}&lang={2}' \
                        .format(self.access_token, open_id, lang)
        response, content = self.http.request(user_info_url, method="GET")

        rlt = json.loads(content)

        if 'errcode' in rlt:
            self.deal_err(rlt)
            return None
        else:
            return rlt

    def decrypt_xml(self, xml, arg_signature, arg_create_time, arg_nonce):
        # crypter = WXBizMsgCrypt(self.token, self.aes_key, self.app_id)
        # rlt, decryp_xml = crypter.DecryptMsg(xml, arg_signature, arg_create_time, arg_nonce)
        # return decryp_xml
        return xml

    def _encrypt_xml(self, xml, create_time):
        # crypter = WXBizMsgCrypt(self.token, self.aes_key, self.app_id)
        # rlt, encrypt_xml = crypter.EncryptMsg(xml, nonce_str(), create_time)
        # if rlt != 0:
        #     print 'WXBizMsgCrypt error:' + str(rlt)
        #     return 'success'    # pass
        #
        # return encrypt_xml
        return xml

    def text_msg(self, to_user, from_user, text, crypt=False):
        create_time = str(int(time.time()))
        xml = '<xml><ToUserName>{0}></ToUserName><FromUserName>{1}></FromUserName><CreateTime>{2}</CreateTime>' \
              '<MsgType>text</MsgType><Content>{3}</Content></xml>'\
              .format(_cdata(to_user), _cdata(from_user), create_time, _cdata(text))
        return self._encrypt_xml(xml, create_time) if crypt else xml

    def news_msg(self, to_user, from_user, news, crypt=False):
        if type(news) is not list and len(news) > 10:
            print 'create news msg error.'
            return 'success'

        create_time = str(int(time.time()))
        xml = '<xml><ToUserName>{0}</ToUserName><FromUserName>{1}</FromUserName><CreateTime>{2}</CreateTime>' \
              '<MsgType>news</MsgType><ArticleCount>{3}</ArticleCount><Articles>'\
              .format(_cdata(to_user), _cdata(from_user), create_time, len(news))

        for new in news:
            xml += '<item><Title>' + _cdata(new['title']) + '</Title>'
            if 'description' in new:
                xml += '<Description>' + _cdata(new['description']) + '</Description>'
            if 'pic_url' in new:
                xml += '<PicUrl>' + _cdata(new['description']) + '</PicUrl>'
            xml += '<Url>' + _cdata(new['url']) + '</Url></item>'

        xml += '</Articles></xml> '

        return self._encrypt_xml(xml, create_time) if crypt else xml

    def deal_err(self, err_rlt):
        if err_rlt['errcode'] == 42001:
            # token 失效
            self.refresh_access_token()

        print err_rlt['errmsg']


class WeixinRefreshATKWorker(threading.Thread):
    def __init__(self, weixin_helper):
        threading.Thread.__init__(self)
        self.weixin_helper = weixin_helper

    def run(self):
        while True:
            while not self.weixin_helper.refresh_access_token():
                time.sleep(5)

            time.sleep(self.weixin_helper.expires_in - 100)


class AccountPropertyNotDefineException(Exception):
    pass

