__author__ = "Franc Hakani"
__version__ = "0.0.1"

import json
import nose
from nose.tools import *

from models import Follower
from models import QuestionTimeNotification
from api import db
from tests import *


def setup_func():
    try:
        newQt = QuestionTimeNotification(tokenid="as23asjdk23")
        db.session.add(newQt)
        db.session.commit()

    except:
        db.session.rollback()


def teardown_func():
    query = QuestionTimeNotification.query.filter_by(
        tokenid="as23asjdk23").first()
    if query is not None:
        db.session.delete(query)
        db.session.commit()


def check_content_type(headers):
    eq_(headers['Content-Type'], 'application/json')


@with_setup(teardown_func)
def test_qt_get():
    # with no data in db
    rv = test_app.get('/questiontime')
    check_content_type(rv.headers)
    resp = json.loads(rv.data)
    eq_(rv.status_code, 200)
    eq_(len(resp), 0)

    # add 1 follow data to db
    setup_func()

    # with 1 data in db
    rv = test_app.get('/questiontime')
    check_content_type(rv.headers)
    resp = json.loads(rv.data)
    eq_(rv.status_code, 200)
    eq_(len(resp), 1)


@with_setup(teardown_func)
def test_qt_post():
    # test create qt
    d = dict(token="as23asjdk23")
    rv = test_app.post('/questiontime', data=d)
    check_content_type(rv.headers)
    eq_(rv.status_code, 201)

    # verfiy
    rv = test_app.get('/questiontime')
    resp = json.loads(rv.data)
    eq_(resp[0]["tokenid"], "as23asjdk23")

    # get test with added qt
    rv = test_app.get('/questiontime')
    check_content_type(rv.headers)
    resp = json.loads(rv.data)
    eq_(rv.status_code, 200)
    eq_(len(resp), 1)

    # create follow again to test error msg
    d = dict(token="as23asjdk23")
    rv = test_app.post('/questiontime', data=d)
    check_content_type(rv.headers)
    eq_(rv.status_code, 500)
    resp = json.loads(rv.data)
    eq_(resp["error"], "Duplicate value")

    # test empty fields for create
    d = dict(token="")
    rv = test_app.post('/questiontime', data=d)
    resp = json.loads(rv.data)
    check_content_type(rv.headers)
    eq_(rv.status_code, 400)
    eq_(resp["error"], "Empty value")


@with_setup(setup_func, teardown_func)
def test_qt_delete():
    # test delete
    d = dict(token="as23asjdk23")
    rv = test_app.delete('/questiontime', data=d)
    eq_(rv.status_code, 204)

    # make sure 0 follows returned
    rv = test_app.get('/questiontime')
    check_content_type(rv.headers)
    resp = json.loads(rv.data)
    eq_(rv.status_code, 200)
    eq_(len(resp), 0)

    # create 1 follow data in db
    setup_func()

    # make sure data is added
    rv = test_app.get('/questiontime')
    check_content_type(rv.headers)
    resp = json.loads(rv.data)
    eq_(rv.status_code, 200)
    eq_(len(resp), 1)

    # delete error for non-existing data msg
    d = dict(token="notindbtoken")
    rv = test_app.delete('/questiontime', data=d)
    eq_(rv.status_code, 500)
    resp = json.loads(rv.data)
    eq_(resp["error"], "Value not found")

    # test empty fields for delete
    d = dict(token="")
    rv = test_app.delete('/questiontime', data=d)
    resp = json.loads(rv.data)
    eq_(rv.status_code, 400)
    eq_(resp["error"], "Empty value")

    # make sure 1 follow data returned, as delete should do nothing with
    # empty fields
    rv = test_app.get('/questiontime')
    check_content_type(rv.headers)
    resp = json.loads(rv.data)
    eq_(rv.status_code, 200)
    eq_(len(resp), 1)
