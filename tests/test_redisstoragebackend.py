#!/usr/bin/env python
"""
UnitTest framework for validating StorageBackends
"""
import os
import base64
try:
    import unittest2 as unittest
except:
    import unittest

try:
    import fakeredis
    from creoconfig import Config
    from creoconfig.redisstoragebackend import RedisStorageBackend
    from test_storagebackend import TestCaseMemStorageBackend


    class TestCaseRedisStorageBackend(TestCaseMemStorageBackend):

        def setUp(self):
            self.s = RedisStorageBackend(connection=fakeredis.FakeStrictRedis)
            self.s.flush()

        def test_flush(self):
            self.assertTrue(self.s.set('mykey', 'myval'))
            self.assertEqual(self.s.get('mykey'), 'myval')
            self.assertEqual(len(self.s), 1)
            self.s.flush()
            self.assertEqual(len(self.s), 0)
            self.assertRaises(KeyError, self.s.get, 'mykey')

        def teardown(self):
            self.s.delete('mykey')
            self.s.delete('234234')
            self.s.delete({'a': 123, 'b': '1231'})


    class TestCaseConfig(unittest.TestCase):

        def setUp(self):
            self.cfg = Config

        def test_redis(self):
            backend = RedisStorageBackend(connection=fakeredis.FakeStrictRedis)
            c = self.cfg(backend=backend)
            self.assertIsInstance(c._store, RedisStorageBackend)
except ImportError:
    print("RedisStorageBackend requires the packages 'redis' and 'fakeredis'!")

if __name__ == '__main__':
    print "INFO: Running tests!"
    unittest.main()

