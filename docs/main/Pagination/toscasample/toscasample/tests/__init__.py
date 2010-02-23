import os
import sys

import webtest
from paste.deploy import loadapp
from routes import url_for
from nose.tools import eq_
from tg import config

from toscasample import model

__all__ = ['url_for', 'TestController']

def setup():
    engine = config['pylons.app_globals'].sa_engine 
    model.init_model(engine)
    model.metadata.create_all(engine)

def teardown():
    engine = config['pylons.app_globals'].sa_engine
    model.metadata.drop_all(engine)

class ModelTest(object):
    klass = None
    attrs = {}

    def setup(self):
        try:
            new_attrs = {}
            new_attrs.update(self.attrs)
            new_attrs.update(self.do_get_dependencies())
            self.obj = self.klass(**new_attrs)
            model.DBSession.add(self.obj)
            model.DBSession.flush()
            return self.obj
        except:
            model.DBSession.rollback()
            raise

    def do_get_dependencies(self):
        return {}

    def test_create_obj(self):
        pass

    def test_query_obj(self):
        obj = model.DBSession.query(self.klass).one()
        for key, value in self.attrs.iteritems():
            eq_(getattr(obj, key), value)

    def teardown(self):
        model.DBSession.rollback()

class TestController(object):
    def __init__(self, *args, **kwargs):
        conf_dir = config.here
        wsgiapp = loadapp('config:test.ini', relative_to=conf_dir)
        self.app = webtest.TestApp(wsgiapp)
