from weixin_helper import WeixinHelper

__author__ = 'nekocode'


class VoteAccount(WeixinHelper):
    def __init__(self, account_config):
        WeixinHelper.__init__(self, account_config)

        self.school_accounts = dict()

    def vote(self, vote_code):
        # todo：做投票操作，并返回相应的错误代码
        pass

    def get_school_account_app_id(self, vote_code):
        pass

    def get_classes_rank(self):
        pass

    def get_person_rank(self):
        pass


class SchoolAccount(WeixinHelper):
    def __init__(self, account_config, vote_account_id):
        WeixinHelper.__init__(self, account_config)

        self.vote_account_id = vote_account_id
        self.classes = dict()

    def get_vote_code(self):
        # todo：获取投票码，并返回相应的错误代码
        pass

    def get_invite_code(self):
        pass

    def get_classes_rank(self):
        pass

    def get_person_rank(self):
        pass


class Class:
    def __init__(self, class_id):
        self.class_id = class_id

        self.voting_count = 0
        self.voting_log = dict()


class People:
    def __init__(self, people_id, voting_count=0):
        self.people_id = people_id
        self.voting_count = voting_count


sub_accounts = {
    '': SchoolAccount({
        'app_id': '',
        'app_secret': '',
        'token': 'nekocode',
        'aes_key': "",
    }, vote_account_id='wxfcc58491aa0b07d6')
}

vote_accounts = {
    'wxfcc58491aa0b07d6': VoteAccount({
        'app_id': 'wxfcc58491aa0b07d6',
        'app_secret': 'd4624c36b6795d1d99dcf0547af5443d',
        'token': 'nekocode',
        'aes_key': "wRR2E0BcY1nrniIe1gf8Otx8DtDG6ibOAYNHZilzakv"
    })
}


