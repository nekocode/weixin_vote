#!/usr/bin/python
# -*- coding: utf-8 -*-
from weixin_helper import WeixinHelper
import torndb

__author__ = 'nekocode'


class VoteAccount(WeixinHelper):
    def __init__(self, account_config):
        WeixinHelper.__init__(self, account_config)

    def vote(self, vote_code, open_id, user_info):
        row = db.get("select * from vote_codes where id=%d" % vote_code)

        if row is None:
            return -1   # 投票码有误

        if row.voted:
            return -2   # 投票码已使用

        row2 = db.query("select * from voted_people where open_id=%s and class_id=%d" % (open_id, row.class_id))

        if len(row2) != 0:
            return -3   # 你已经为该班级投过票了

        # 销毁投票码 & 班级总票数 + 1
        db.update("update vote_codes set voted=true where id=%d" % vote_code)
        db.update("update classes set voting_count=voting_count+1 where id=%d" % row.class_id)

        # 校园总票数 +1
        class_row = db.get("select * from classes where id=%d" % row.class_id)
        school_account_id = class_row.school_account_id
        db.update("update school_accounts set voting_count=voting_count+1 where app_id=%s" % school_account_id)
        school_accounts[school_account_id].voting_count += 1

        # 添加个人投票记录，并返回 invite_id
        row_id = db.insert("insert into voted_people(open_id, nickname, avatar_url, inviting_count, "
                           "class_id, school_account_id) "
                           "values('%s','%s', '%s', %d, %d, %s)" %
                           (open_id, user_info['nickname'], user_info['headimgurl'], 0,
                            row.class_id, self.app_id))

        # 是邀请而来的话，邀请人邀请数 +1
        if row.invite_id is not None:
            db.update("update voted_people set inviting_count=inviting_count+1 where id=%d" % row.invite_id)

        return row_id   # 返回邀请码

    @staticmethod
    def get_school_account_app_id(vote_code):
        row = db.get("select * from vote_codes where id=%d" % vote_code)
        school_account = db.get("select * from classes where id=%d" % row.class_id)

        return school_account.app_id


class SchoolAccount(WeixinHelper):
    def __init__(self, account_config, vote_account_id, school_name, avatar_url, voting_count):
        WeixinHelper.__init__(self, account_config)

        self.vote_account_id = vote_account_id
        self.school_name = school_name
        self.avatar_url = avatar_url
        self.voting_count = voting_count

    @staticmethod
    def get_vote_code(code_with_prefix):
        try:
            if code_with_prefix.startwith('C'):
                class_id = int(code_with_prefix[1:])
                row_id = db.insert("insert to vote_codes(class_id, voted) values(%d, false)" % class_id)
                return row_id   # 返回投票码

            else:   # start with 'I' 是邀请码的话
                invite_id = int(code_with_prefix[1:])
                row = db.get("select * from voted_people where id=%d" % invite_id)
                row_id = db.insert("insert to vote_codes(class_id, voted, invite_id) values(%d, false, %d)" %
                                   (row.class_id, invite_id))
                return row_id   # 返回投票码

                pass
        except ValueError:
            return None

    def get_classes_rank(self):
        rows = db.query("select * from classes where school_account_id=%s order by voting_count desc" % self.app_id)
        return rows

    def get_person_rank(self):
        rows = db.query("select * from voted_people where school_account_id=%s order by inviting_count desc" %
                        self.app_id)
        return rows


class Class:
    def __init__(self, class_id, class_name, voting_count, school_acount_id):
        self.class_id = class_id
        self.class_name = class_name
        self.voting_count = voting_count
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
        }, account.vote_account_id, account.school_name, account.avatar_url, account.voting_count)

        school_accounts[account.app_id] = school_account


def create_tables():
    if if_table_exist('vote_accounts') == 0:
        db.execute("create table vote_accounts(app_id VARCHAR(20) PRIMARY KEY, app_secret VARCHAR(40) NOT NULL, "
                   "token VARCHAR(20) NOT NULL, aes_key VARCHAR(60) NOT NULL)")

    if if_table_exist('school_accounts') == 0:
        db.execute("create table school_accounts(app_id VARCHAR(20) PRIMARY KEY, app_secret VARCHAR(40) NOT NULL, "
                   "token VARCHAR(20) NOT NULL, aes_key VARCHAR(60) NOT NULL, "
                   "vote_account_id VARCHAR(20) NOT NULL, school_name VARCHAR(60), avatar_url VARCHAR(512), "
                   "voting_count INTEGER)")

    if if_table_exist('classes') == 0:
        # 使用 id 做班级码
        db.execute("create table classes(id INTEGER PRIMARY KEY AUTO_INCREMENT, class_name VARCHAR(60), "
                   "voting_count INTEGER, school_account_id VARCHAR(20) NOT NULL)")

    if if_table_exist('voted_people') == 0:
        # 使用 id 做邀请码
        db.execute("create table voted_people(id INTEGER PRIMARY KEY AUTO_INCREMENT, open_id VARCHAR(128) NOT NULL, "
                   "nickname VARCHAR(60), avatar_url VARCHAR(512), inviting_count INTEGER, "
                   "class_id INTEGER, school_account_id VARCHAR(20) NOT NULL)")

    if if_table_exist('vote_codes') == 0:
        # 使用 id 做投票码
        db.execute("create table vote_codes(id INTEGER PRIMARY KEY AUTO_INCREMENT, "
                   "class_id INTEGER, voted BOOLEAN, invite_id INTEGER)")


def if_table_exist(table_name):
    count = db.get("select count(*) as count from information_schema.tables "
                   "where table_schema ='app_nekocode' and table_name ='" + table_name + "'")
    return count.count


if __name__ == '__main__':
    init_db()

