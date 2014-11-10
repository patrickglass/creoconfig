#!/usr/bin/env python
"""
UnitTest framework for validating StorageBackends
"""
import os
import unittest
from creoconfig.storagebackend import *


class TestCaseStorageBackend(unittest.TestCase):

    def test_using_abstract_class(self):
        s = StorageBackend()
        self.assertRaises(NotImplementedError, s.set, 'mykey', 'myval')
        self.assertRaises(NotImplementedError, s.get, 'mykey', 'mydefault')
        self.assertRaises(NotImplementedError, s.delete, 'mykey')


class TestCaseMemStorageBackend(unittest.TestCase):

    def setUp(self):
        self.s = MemStorageBackend()

    def test_set(self):
        self.assertTrue(self.s.set('mykey', 'myval'))

    def test_get_exists(self):
        self.assertTrue(self.s.set('mykey', 'myval'))
        self.assertEqual(self.s.get('mykey', 'defaultvalue'), 'myval')

    def test_get_not_exists(self):
        self.assertTrue(self.s.set('mykey', 'myval'))
        self.assertEqual(self.s.get('badkey', 'defaultvalue'), 'defaultvalue')

    def test_delete_exists(self):
        self.assertTrue(self.s.set('mykey', 'myval'))
        self.assertEqual(self.s.get('mykey', 'defaultvalue'), 'myval')
        self.assertTrue(self.s.delete('mykey'))
        self.assertEqual(self.s.get('mykey', 'defaultvalue'), 'defaultvalue')

    def test_delete_not_exists(self):
        self.assertFalse(self.s.delete('mykey'))

    def test_object_key(self):
        mykey = object()
        self.assertTrue(self.s.set(mykey, 'myval'))
        self.assertEqual(self.s.get(mykey, 'defaultvalue'), 'myval')

    def test_object_value(self):
        mykey = '234234'
        myval = object()
        self.assertTrue(self.s.set(mykey, myval))
        self.assertEqual(self.s.get(mykey, 'defaultvalue'), myval)

    def test_int_str_key(self):
        self.assertTrue(self.s.set(123, 'myval'))
        self.assertEqual(self.s.get('123', 'defaultvalue'), 'defaultvalue')


class TestCaseFileStorageBackend(unittest.TestCase):

    def setUp(self):
        self.filename = 'tmp.config'
        self.s = FileStorageBackend(filename=self.filename)

    def test_set(self):
        self.assertTrue(self.s.set('mykey', 'myval'))

    def test_get_exists(self):
        self.assertTrue(self.s.set('mykey', 'myval'))
        self.assertEqual(self.s.get('mykey', 'defaultvalue'), 'myval')

    def test_get_not_exists(self):
        self.assertTrue(self.s.set('mykey', 'myval'))
        self.assertEqual(self.s.get('badkey', 'defaultvalue'), 'defaultvalue')

    def test_delete_exists(self):
        self.assertTrue(self.s.set('mykey', 'myval'))
        self.assertEqual(self.s.get('mykey', 'defaultvalue'), 'myval')
        self.assertTrue(self.s.delete('mykey'))
        self.assertEqual(self.s.get('mykey', 'defaultvalue'), 'defaultvalue')

    def test_delete_not_exists(self):
        self.assertFalse(self.s.delete('mykey'))

    def test_object_key(self):
        mykey = object()
        self.assertRaises(TypeError, self.s.set, mykey, 'myval')

    def test_object_value(self):
        mykey = '234234'
        myval = {'a': 123, 'b': '1231'}
        self.assertTrue(self.s.set(mykey, myval))
        self.assertEqual(self.s.get(mykey, 'defaultvalue'), myval)

    def test_close(self):
        self.assertEqual(self.s.close(), None)

    def tearDown(self):
        self.s.close()
        del self.s
        try:
            os.remove(self.filename + '.os')
        except:
            pass


# @unittest.skip("Redis Backend Requires Server")
class TestCaseRedisStorageBackend(unittest.TestCase):

    def setUp(self):
        self.s = RedisStorageBackend()

    def test_set(self):
        self.assertTrue(self.s.set('mykey', 'myval'))

    def test_get_exists(self):
        self.assertTrue(self.s.set('mykey', 'myval'))
        self.assertEqual(self.s.get('mykey', 'defaultvalue'), 'myval')

    def test_get_not_exists(self):
        self.assertTrue(self.s.set('mykey', 'myval'))
        self.assertEqual(self.s.get('badkey', 'defaultvalue'), 'defaultvalue')

    def test_delete_exists(self):
        self.assertTrue(self.s.set('mykey', 'myval'))
        self.assertEqual(self.s.get('mykey', 'defaultvalue'), 'myval')
        self.assertTrue(self.s.delete('mykey'))
        self.assertEqual(self.s.get('mykey', 'defaultvalue'), 'defaultvalue')

    def test_delete_not_exists(self):
        self.assertFalse(self.s.delete('mykey'))

    def test_dict_key(self):
        mykey = {'a': 123, 'b': '1231'}
        self.assertTrue(self.s.set(mykey, 'myval'))
        self.assertEqual(self.s.get(mykey, 'defaultvalue'), 'myval')

    def test_object_value(self):
        mykey = '234234'
        myval = {'a': 123, 'b': '1231'}
        self.assertTrue(self.s.set(mykey, myval))
        self.assertEqual(self.s.get(mykey, 'defaultvalue'), str(myval))

    def test_int_str_key(self):
        """Redis does not differentiate between storing strings or ints."""
        self.assertTrue(self.s.set(123, 'myval'))
        self.assertEqual(self.s.get('123', 'defaultvalue'), 'myval')

    def teardown(self):
        self.s.delete('mykey')
        self.s.delete('234234')
        self.s.delete({'a': 123, 'b': '1231'})


if __name__ == '__main__':
    print "INFO: Running tests!"
    unittest.main()

