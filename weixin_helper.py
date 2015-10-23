#!/usr/bin/python
# -*- coding: utf-8 -*-

import hashlib
import json
import threading
import time
import httplib2
from xml.etree import cElementTree
from weixin_crypt.WXBizMsgCrypt import WXBizMsgCrypt

__author__ = 'nekocode'


def xml2dict(self, xml):
    # 将 xml 转为 dict
    return dict((child.tag, child.text) for child in cElementTree.fromstring(xml))


class WeixinHelper:
    def __init__(self, app_id, app_secret, token, aes_key):
        self.app_id = app_id
        self.app_secret = app_secret
        self.token = token
        self.aes_key = aes_key

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
            return False
        else:
            self.access_token = rlt['access_token']
            self.expires_in = rlt['expires_in']
            return True

    def decrypt_msg(self):
        pass

    def encrypt_msg(self):
        crypter = WXBizMsgCrypt(self.token, self.aes_key, self.app_id)
        rlt, encrypt_xml = crypter.EncryptMsg("xml", int(time.time()))
        return encrypt_xml


class WeixinRefreshATKWorker(threading.Thread):
    def __init__(self, weixin_helper):
        threading.Thread.__init__(self)
        self.weixin_helper = weixin_helper

    def run(self):
        while True:
            self.weixin_helper.refresh_access_token()
            time.sleep(7000)

