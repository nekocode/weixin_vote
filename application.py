#!/usr/bin/env python
# coding:utf-8
from url import url
import tornado.web
import os
from uimodule import uimodules


setting = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "template_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "61oETzKXQAGaYdk12345GeJJFuYh7EQnp2XdTP1o/Vo=",
    "login_url": "/login",
    "ui_modules": uimodules,
}


application = tornado.web.Application(
    handlers=url,
    **setting
)

