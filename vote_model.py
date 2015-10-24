__author__ = 'nekocode'


class Class:
    def __init__(self, class_id, school, voting_count=0, voted_peoples=list()):
        self.class_id = class_id
        self.school = school
        self.voting_count = voting_count
        self.voted_peoples = voted_peoples


class People:
    def __init__(self, people_id, voting_count=0):
        self.people_id = people_id
        self.voting_count = voting_count

