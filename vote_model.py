from weixin_helper import WeixinHelper

__author__ = 'nekocode'


class VoteAccount(WeixinHelper):
    def __init__(self, account, school_accounts=None):
        WeixinHelper.__init__(self, account)
        self.school_accounts = school_accounts if school_accounts is not None else dict()

    def vote(self, vote_code):
        # todo：做投票操作，并返回相应的错误代码
        pass


class SchoolAccount(WeixinHelper):
    def __init__(self, account, vote_account_id, classes=None):
        WeixinHelper.__init__(self, account)
        self.vote_account_id = vote_account_id
        self.classes = classes if classes is not None else dict()

    def get_classes_rank(self):
        pass

    def get_person_rank(self):
        pass


class Class:
    def __init__(self, class_id, sub_account_id, voting_count=0, voted_peoples=None):
        self.class_id = class_id
        self.school = sub_account_id
        self.voting_count = voting_count
        self.voted_peoples = voted_peoples if voted_peoples is not None else dict()


class People:
    def __init__(self, people_id, voting_count=0):
        self.people_id = people_id
        self.voting_count = voting_count

