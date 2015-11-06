#!/usr/bin/python
# -*- coding: utf-8 -*-
import tornado
import tornado.web

__author__ = 'nekocode'


class SideBar(tornado.web.UIModule):
    def render(self, select):
        return self.render_string(
            "static/admin/modules/side-bar.html", select=select)


class Footer(tornado.web.UIModule):
    def render(self):
        return self.render_string(
            "static/admin/modules/footer.html", desc=u"学壹传媒")


