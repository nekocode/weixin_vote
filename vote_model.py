#!/usr/bin/python
# -*- coding: utf-8 -*-
from weixin_helper import WeixinHelper
import torndb

__author__ = 'nekocode'


class VoteAccount(WeixinHelper):
    def __init__(self, account_config):
        WeixinHelper.__init__(self, account_config)

        self.school_accounts = dict()

    @staticmethod
    def vote(vote_code, open_id, nick_name, avatar_url):
        if vote_code not in vote_codes:
            return -1   # 投票码有误

        class_id = vote_codes[vote_code].class_id
        vote_codes[vote_code].voted = True
        db.update("update vote_codes vc set vc.voted = true where vc.class_id=%d" % class_id)

        classes[class_id].voting_count += 1
        db.update("update classes cl set cl.voting_count = cl.voting_count+1 where cl.id=%d" % class_id)

        # todo: voted_people 也要做处理 !!!!
        invite_id = db.insert("insert ")
        vote_peoples[open_id] = VotedPeople(invite_id, open_id)

        return 0

    @staticmethod
    def get_school_account_app_id(vote_code):
        class_id = vote_codes[vote_code].class_id
        _class = classes[class_id]
        school_account = school_accounts[_class.school_acount_id]
        return school_account.app_id


class SchoolAccount(WeixinHelper):
    def __init__(self, account_config, vote_account_id, school_name, avatar_url):
        WeixinHelper.__init__(self, account_config)

        self.vote_account_id = vote_account_id
        self.school_name = school_name
        self.avatar_url = avatar_url
        self.classes = dict()

    def get_vote_code(self):
        # todo：获取投票码
        pass

    def get_invite_code(self):
        pass

    def get_classes_rank(self):
        pass

    def get_person_rank(self):
        pass


class Class:
    def __init__(self, class_id, class_name, voting_count, school_acount_id):
        self.class_id = class_id
        self.class_name = class_name
        self.voting_count = voting_count
        self.voted_people = dict()
        self.school_acount_id = school_acount_id


class VotedPeople:
    def __init__(self, invite_id, open_id, nickname, avatar_url, inviting_count, class_id):
        self.invite_id = invite_id
        self.open_id = open_id
        self.nickname = nickname
        self.avatar_url = avatar_url
        self.inviting_count = inviting_count
        self.class_id = class_id


school_accounts = dict()
vote_accounts = dict()
classes = dict()
vote_peoples = dict()
vote_codes = dict()     # class_id, voted
db = None


def init_db():
    global db
    db = torndb.Connection('localhost', 'app_nekocode', 'root', 'root')

    create_tables()

    rlt = db.query("select * from vote_accounts")
    for account in rlt:
        vote_accounts[account.app_id] = VoteAccount({
            'app_id': account.app_id,
            'app_secret': account.app_secret,
            'token': account.token,
            'aes_key': account.aes_key
        })

    rlt = db.query("select * from school_accounts")
    for account in rlt:
        school_account = SchoolAccount({
            'app_id': account.app_id,
            'app_secret': account.app_secret,
            'token': account.token,
            'aes_key': account.aes_key
        }, account.vote_account_id, account.school_name, account.avatar_url)

        school_accounts[account.app_id] = school_account
        vote_accounts[account.vote_account_id].school_accounts[account.app_id] = school_account

    rlt = db.query("select * from classes")
    for class_info in rlt:
        _class = Class(class_info.id, class_info.class_name, class_info.voting_count, class_info.school_account_id)

        classes[_class.class_id] = _class
        school_accounts[class_info.school_account_id].classes[class_info.id] = _class

    rlt = db.query("select * from voted_people")
    for voted_people_info in rlt:
        voted_people = VotedPeople(voted_people_info.id, voted_people_info.open_id, voted_people_info.nickname,
                                   voted_people_info.avatar_url, voted_people_info.inviting_count, voted_people_info.class_id)

        vote_peoples[voted_people_info.id] = voted_people
        classes[voted_people_info.class_id].voted_people[voted_people_info.id] = voted_people

    rlt = db.query("select * from vote_codes")
    for vote_code in rlt:
        vote_codes[vote_code.id] = vote_code


def create_tables():
    if if_table_exist('vote_accounts') == 0:
        db.execute("create table vote_accounts(app_id VARCHAR(20) PRIMARY KEY, app_secret VARCHAR(40) NOT NULL, "
                   "token VARCHAR(20) NOT NULL, aes_key VARCHAR(60) NOT NULL)")

    if if_table_exist('school_accounts') == 0:
        db.execute("create table school_accounts(app_id VARCHAR(20) PRIMARY KEY, app_secret VARCHAR(40) NOT NULL, "
                   "token VARCHAR(20) NOT NULL, aes_key VARCHAR(60) NOT NULL, "
                   "vote_account_id VARCHAR(20) NOT NULL, school_name VARCHAR(60), avatar_url VARCHAR(512))")

    if if_table_exist('classes') == 0:
        # 使用 id 做班级码
        db.execute("create table classes(id INTEGER PRIMARY KEY AUTO_INCREMENT, class_name VARCHAR(60), "
                   "voting_count INTEGER, school_account_id VARCHAR(20) NOT NULL)")

    if if_table_exist('voted_people') == 0:
        # 使用 id 做邀请码
        db.execute("create table voted_people(id INTEGER PRIMARY KEY AUTO_INCREMENT, open_id VARCHAR(128) NOT NULL, "
                   "nickname VARCHAR(60), avatar_url VARCHAR(512), inviting_count INTEGER, class_id INTEGER)")

    if if_table_exist('vote_codes') == 0:
        # 使用 id 做投票码
        db.execute("create table vote_codes(id INTEGER PRIMARY KEY AUTO_INCREMENT, class_id INTEGER, voted BOOLEAN)")


def if_table_exist(table_name):
    count = db.get("select count(*) as count from information_schema.tables "
                   "where table_schema ='app_nekocode' and table_name ='" + table_name + "'")
    return count.count


if __name__ == '__main__':
    init_db()

