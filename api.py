__author__ = "Franc Hakani"
__version__ = "0.0.2"

from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from apns import APNs, Frame, Payload
import os
from flask.ext.sqlalchemy import SQLAlchemy
import time
from sqlalchemy.exc import IntegrityError
from SOAPpy import WSDL
from flask.ext.cache import Cache
import urllib
import flask
#cache = Cache(config={'CACHE_TYPE': 'simple'})
apns = APNs(use_sandbox=True,
            cert_file='cert.pem',
            key_file='key.pem',
            enhanced=True)
app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)
api = Api(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
from models import *

parser = reqparse.RequestParser()
parser.add_argument('bill')
parser.add_argument('token')


class Follow(Resource):
    """
    REST api with URI /follow that premits only get, post, and delete
    HTTP requests. It interacts with the 'Follower' database table model.
    """

    def get(self):
        """
        get HTTP method

        Query the database for all data inside the 'Follower' table.

        Returns:
            A dict of the result of the query and a 200 OK HTTP status code.
        """
        followresult = Follower.query.all()
        results = []
        for item in followresult:
            results.append(item.as_dict())
        return results, 200

    def post(self):
        """
        post HTTP method

        Add data value of bill and token to 'Follower' table in database.

        HTTP args:
            bill -- The name of the bill
            token -- The tokenid of the device to be added with the bill

        Returns:
            If error not raised, A dict of the billname & token and a 201
            Created HTTP status code. Otherwise a dict with
            error: "Duplicate value" and a 500 Internal Server Error HTTP
            status code.

        Raises:
            SQLAlchemy.IntegrityError: Duplicate value violates unique
            constraint with 'Follower' database model.
        """
        args = parser.parse_args()
        billname = args['bill']
        token = args['token']
        if billname == "" or token == "":
            return dict(error="Empty value"), 400
        token = token.encode('ascii')
        try:
            newFollow = Follower(billname=billname, tokenid=token)
            db.session.add(newFollow)
            db.session.commit()
            return newFollow.as_dict(), 201
        except IntegrityError:
            db.session.rollback()
            return dict(error="Duplicate value"), 500

    def delete(self):
        """
        delete HTTP method

        Delete value of bill and token from 'Follower' table in database.

        HTTP args:
            bill -- The name of the bill
            token -- the tokenid of the device to be added with the bill

        Returns:
            If value not in database, A dict with
            error: "Value not found" and 500 Internal Service Error
            HTTP status code. Otherwise a 204 No Content HTTP status code.
        """
        args = parser.parse_args()
        billname = args['bill']
        token = args['token']
        if billname == "" or token == "":
            return dict(error="Empty value"), 400
        token = token.encode('ascii')
        query = Follower.query.filter_by(billname=billname,
                                         tokenid=token).first()
        if query is None:
            return dict(error="Value not found"), 500
        else:
            db.session.delete(query)
            db.session.commit()
            return "", 204


class QuestionTime(Resource):
    """
    REST api with URI /questiontime that premits only get, post, and delete
    HTTP requests. It interacts with the 'QuestionTimeNotification' database
    table model.
    """

    def get(self):
        """
        get HTTP method

        Query the database for all data inside the 'QuestionTimeNotification'
        table.

        Returns:
            A dict of the result of the query and a 200 OK HTTP status code.
        """
        qtquery = QuestionTimeNotification.query.all()
        results = []
        for item in qtquery:
            results.append(item.as_dict())
        return results, 200

    def post(self):
        """
        post HTTP method

        Add data value of token to 'QuestionTimeNotification'
        table in database.

        HTTP args:
            token -- The tokenid of the device to be added

        Returns:
            If error not raised, A dict token and a 201
            Created HTTP status code. Otherwise a dict with
            error: "Duplicate value" and a 500 Internal Server Error HTTP
            status code.

        Raises:
            SQLAlchemy.IntegrityError: Duplicate value violates unique
            constraint with 'QuestionTimeNotification' database model.
        """
        args = parser.parse_args()
        token = args['token']
        if token == "":
            return dict(error="Empty value"), 400
        token = token.encode('ascii')
        try:
            newQT = QuestionTimeNotification(tokenid=token)
            db.session.add(newQT)
            db.session.commit()
            return newQT.as_dict(), 201
        except IntegrityError:
            db.session.rollback()
            return dict(error="Duplicate value"), 500

    def delete(self):
        """
        delete HTTP method

        Delete value of token from 'QuestionTimeNotification' table in database.

        HTTP args:
            token -- the tokenid of the device to be added with the bill

        Returns:
            If value not in database, A dict with
            error: "Value not found" and 500 Internal Service Error
            HTTP status code. Otherwise a 204 No Content HTTP status code.
        """
        args = parser.parse_args()
        token = args['token']
        if token == "":
            return dict(error="Empty value"), 400
        token = token.encode('ascii')
        query = QuestionTimeNotification.query.filter_by(tokenid=token).first()
        if query is None:
            return dict(error="Value not found"), 500
        else:
            db.session.delete(query)
            db.session.commit()
            return "", 204


class SendQuestionTimeNotfication(Resource):
    """
    REST api with URI /notification/questiontime that premits a post
    HTTP request.
    It interacts with the 'QuestionTimeNotification' database table model.
    """

    def post(self):
        """
        post HTTP method

        Send apns notification for all data in the QuestionTimeNotification
        table.

        Returns:
            A 201 Created HTTP status code.
        """
        query = QuestionTimeNotification.query.all()
        print query
        if len(query) < 1:
            return "", 500
        else:
            payload = Payload(
                alert="Question time is currently live.",
                sound="default",
                category="QUESTION_TIME_CATEGORY",
                custom={
                    'link':
                    'http:/a-vide-link/playlist.m3u8'
                },
                badge=0)
            frame = Frame()
            identifer = 1
            expiry = time.time() + 3600
            priority = 10
            for item in query:
                token_hex = ''.join(item.tokenid)
                frame.add_item(token_hex, payload, identifer, expiry, priority)
            apns.gateway_server.send_notification_multiple(frame)
            return "", 204


class SendBillNotification(Resource):
    """
    REST api with URI /notification that premits a post HTTP request.
    It interacts with the 'Follower' database table model.
    """

    def post(self):
        """
        post HTTP method

        Send apns notification for given devices in 'Follower' table
        associated with bill argument.

        HTTP args:
            bill -- The name of the bill

        Returns:
            A 201 Created HTTP status code.
        """
        args = parser.parse_args()
        billname = args['bill']
        query = Follower.query.filter_by(billname=billname).all()
        print query
        if len(query) < 1:
            return "", 500
        else:
            payload = Payload(
                alert=billname + " is currently live.",
                sound="default",
                category="BILLS_CATEGORY",
                custom={
                    'link':
                    'http:/a-vide-link/playlist.m3u8'
                },
                badge=0)
            frame = Frame()
            identifer = 1
            expiry = time.time() + 3600
            priority = 10
            for item in query:
                token_hex = ''.join(item.tokenid)
                frame.add_item(token_hex, payload, identifer, expiry, priority)
            apns.gateway_server.send_notification_multiple(frame)
            return "", 204


def cache_key():
    args = flask.request.args
    key = flask.request.path + '?' + urllib.urlencode([
        (k, v) for k in sorted(args) for v in sorted(args.getlist(k))
    ])
    return key


class Bill:
    def __init__(self, type, no, name):
        self.type = type
        self.no = no
        self.name = name

    def as_dict(self):
        return {
            "BillType": self.type,
            "BillNo": self.no,
            "BillName": self.name
        }


api.add_resource(SendBillNotification, '/notification')
api.add_resource(SendQuestionTimeNotfication, '/notification/questiontime')
api.add_resource(Follow, '/follow')
api.add_resource(QuestionTime, '/questiontime')

if __name__ == '__main__':
    app.run(debug=True)
