#!/usr/bin/python
# -*- coding: utf-8 -*-
from tornado.web import RequestHandler

import config
from model.vote_model import school_accounts, vote_accounts


class VoteCodeHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, app_id):
        if app_id not in vote_accounts:
            self.write('打开姿势有误 ╮(╯_╰)╭')
            return
        account = vote_accounts[app_id]

        vote_code = 'V%05d' % int(self.get_argument('vc'))
        qrcode_url = account.qrcode_url
        account_name = account.name
        account_id = account.display_id

        self.render("vote/vote_code.html", vote_code=vote_code, qrcode_url=qrcode_url,
                    account_name=account_name, account_id=account_id)


class QRCodeHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, app_id):
        account = None
        if app_id in vote_accounts:
            account = vote_accounts[app_id]
        elif app_id in school_accounts:
            account = school_accounts[app_id]
        else:
            self.write('打开姿势有误 ╮(╯_╰)╭')
            return

        qrcode_url = account.qrcode_url
        account_name = account.name
        account_id = account.display_id

        self.render("vote/qrcode.html", qrcode_url=qrcode_url,
                    account_name=account_name, account_id=account_id)


class InviteCodeHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, invite_code):
        invite_code = 'I%05d' % int(invite_code)

        self.render("vote/invite_code.html", invite_code=invite_code)


class RankHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, app_id):
        if app_id not in school_accounts:
            self.write('打开姿势有误 ╮(╯_╰)╭')
            return
        account = school_accounts[app_id]
        vote_account_id = account.vote_account_id

        # 获取所有同一个大号的所有小号的排名
        vote_total_count = 0
        class_rank_rows = []
        person_rank_rows = []
        for sc in school_accounts.values():
            if sc.vote_account_id == vote_account_id:
                vote_total_count += sc.voting_count
                class_rank_rows.extend(sc.get_classes_rank())
                person_rank_rows.extend(sc.get_person_rank())

        # 对列表进行排名
        sorted(class_rank_rows, key=lambda e: e.voting_count, reverse=True)
        sorted(person_rank_rows, key=lambda e: e.inviting_count, reverse=True)
        person_rank_rows = person_rank_rows[:20]

        avatar_url = vote_accounts[vote_account_id].avatar_url
        qrcode_url = config.DOMAIN + '/qrcode/' + account.app_id
        school_name = account.school_name
        class_count = len(class_rank_rows)

        self.render("vote/ranking.html",
                    class_rank_rows=class_rank_rows, person_rank_rows=person_rank_rows,
                    avatar_url=avatar_url, qrcode_url=qrcode_url, school_name=school_name, class_count=class_count,
                    vote_total_count=vote_total_count)


