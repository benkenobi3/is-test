import os
import app
import unittest
import fakeredis
from unittest import mock
from datetime import datetime, timedelta

HEADERS = {'X-Forwarded-For':'192.168.10.10'}
HEADERS_SAME_SUBNET = {'X-Forwarded-For':'192.168.10.57'}
HEADERS_DIFF_SUBNET = {'X-Forwarded-For':'192.168.56.10'}

class FlaskTestCase(unittest.TestCase):

    @mock.patch('app.red', fakeredis.FakeRedis(server=fakeredis.FakeServer()))
    def setUp(self):
        self.app = app.app.test_client()
        
    def tearDown(self):
        pass

    @mock.patch('app.red', fakeredis.FakeRedis(server=fakeredis.FakeServer()))
    def test_connection(self):
        r = self.app.get('/')
        assert '400' in r.status
        r = self.app.get('/', headers=HEADERS)
        assert '200' in r.status

    @mock.patch('app.red', fakeredis.FakeRedis(server=fakeredis.FakeServer()))
    def test_limit(self):
        for i in range(100):
            r = self.app.get('/', headers=HEADERS)
            assert '200' in r.status
        r = self.app.get('/', headers=HEADERS)
        assert '429' in r.status

    @mock.patch('app.red', fakeredis.FakeRedis(server=fakeredis.FakeServer()))
    @mock.patch('app.LIMIT', 10)
    @mock.patch('app.INTERVAL', 10)
    @mock.patch('app.TIMEOUT', 20)
    def test_timeout_time(self):

        for i in range(9):
            r = self.app.get('/', headers=HEADERS)
        
        start_time = datetime.now() + timedelta(seconds=app.TIMEOUT)
        r = self.app.get('/', headers=HEADERS)

        while ('200' not in r.status):
            r = self.app.get('/', headers=HEADERS)

        assert datetime.now() - start_time < timedelta(milliseconds=1)

    @mock.patch('app.red', fakeredis.FakeRedis(server=fakeredis.FakeServer()))
    def test_diff_ip_in_subnet_limit(self):
        for i in range(80):
            r = self.app.get('/', headers=HEADERS)
            assert '200' in r.status
        for i in range(20):
            r = self.app.get('/', headers=HEADERS_SAME_SUBNET)
            assert '200' in r.status
        r = self.app.get('/', headers=HEADERS)
        assert '429' in r.status

    @mock.patch('app.red', fakeredis.FakeRedis(server=fakeredis.FakeServer()))
    def test_diff_subnet_limit(self):
        for i in range(80):
            r = self.app.get('/', headers=HEADERS)
            assert '200' in r.status
        for i in range(20):
            r = self.app.get('/', headers=HEADERS_DIFF_SUBNET)
            assert '200' in r.status
        r = self.app.get('/', headers=HEADERS)
        assert '200' in r.status

if __name__ == '__main__':
    unittest.main()