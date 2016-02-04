__author__ = "Franc Hakani"
__version__ = "0.0.1"

from api import db


class Follower(db.Model):
    __tablename__ = 'followers'

    id = db.Column(db.Integer, primary_key=True)
    billname = db.Column(db.String())
    tokenid = db.Column(db.String())

    __table_args__ = (db.UniqueConstraint('billname',
                                          'tokenid',
                                          name='_bill_location'), )

    def __init__(self, billname, tokenid):
        self.billname = billname
        self.tokenid = tokenid

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class QuestionTimeNotification(db.Model):
    __tablename__ = 'questiontimenotifications'

    id = db.Column(db.Integer, primary_key=True)
    tokenid = db.Column(db.String(), unique=True)

    def __init__(self, tokenid):
        self.tokenid = tokenid

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
