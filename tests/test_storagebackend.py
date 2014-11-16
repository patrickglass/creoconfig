#!/usr/bin/env python
"""
UnitTest framework for validating StorageBackends
"""
import os
import base64
import fakeredis
try:
    import unittest2 as unittest
except:
    import unittest
from creoconfig.storagebackend import *


class TestCaseMemStorageBackend(unittest.TestCase):

    def setUp(self):
        self.s = MemStorageBackend()

    def test_set(self):
        self.assertTrue(self.s.set('mykey', 'myval'))

    def test_contains_in(self):
        self.s.set('mykey', 'myval')
        self.assertTrue('mykey' in self.s)

    def test_get_exists(self):
        self.assertTrue(self.s.set('mykey', 'myval'))
        self.assertEqual(self.s.get('mykey'), 'myval')

    def test_get_not_exists(self):
        self.assertTrue(self.s.set('mykey', 'myval'))
        self.assertRaises(KeyError, self.s.get, 'badkey')

    def test_delete_exists(self):
        self.assertTrue(self.s.set('mykey', 'myval'))
        self.assertEqual(self.s.get('mykey'), 'myval')
        self.s.delete('mykey')
        self.assertRaises(KeyError, self.s.get, 'mykey')

    def test_delete_not_exists(self):
        self.assertRaises(KeyError, self.s.delete, 'mykey')

    def test_int_key(self):
        self.assertTrue(self.s.set(123, 'myval'))
        # self.assertRaises(KeyError, self.s.get, '123')
        self.assertEqual(self.s.get(123), 'myval')

    @unittest.skip("We should not allow objects as keys. FIXME throw error in Backends.")
    def test_object_key(self):
        mykey = object()
        # self.assertTrue(self.s.set(mykey, 'myval'))
        # self.assertEqual(self.s.get(mykey), 'myval')
        self.assertRaises(AttributeError, self.s.set, mykey, 'myval')
        self.assertRaises(AttributeError, self.s.set, mykey, 'myval2')
        self.assertRaises(AttributeError, self.s.set, mykey, 'myval3')

    def test_dict_value(self):
        # Check that we are able to store a complex value type
        # since most backends only support string we will return
        # a string type no matter what was saved.
        mykey = '234234'
        myval = {
            'spot': 'likes to run',
            'kind': 1234,
            'cmplx': (1, 2, 3, '123')
        }
        self.assertTrue(self.s.set(mykey, myval))
        self.assertEqual(str(self.s.get(mykey)), str(myval))

    def test_len(self):
        self.assertEqual(len(self.s), 0)
        self.assertTrue(self.s.set('mykey', 'myval'))
        self.assertEqual(len(self.s), 1)
        self.assertTrue(self.s.set('mykey2', 'myval2'))
        self.assertEqual(len(self.s), 2)
        self.assertTrue(self.s.set('mykey', 'myval'))
        self.assertEqual(len(self.s), 2)
        self.s.delete('mykey')
        self.assertEqual(len(self.s), 1)
        self.assertTrue(self.s.set('mykey', 'myval'))
        self.assertEqual(len(self.s), 2)
        self.assertTrue(self.s.set('mykey3', 'myval3'))
        self.assertEqual(len(self.s), 3)

    def test_iter(self):
        self.s.set('mykey', 'myval')
        self.s.set('mykey2', 'myval2')
        self.s.set('mykey', 'myval')
        self.s.delete('mykey')
        self.s.set('mykey', 'myval4')
        self.s.set('mykey3', 'myval3')
        self.assertItemsEqual(self.s.items(),
            [
                ('mykey', 'myval4'),
                ('mykey2', 'myval2'),
                ('mykey3', 'myval3'),
            ]
        )
        i = iter(self.s)
        items = [i.next(), i.next(), i.next()]
        self.assertItemsEqual(items,
            ['mykey', 'mykey2', 'mykey3'])
        self.assertRaises(StopIteration, i.next)
        i = iter(self.s)
        for k,v in self.s.iteritems():
            self.assertTrue((k, v))


class TestCaseFileStorageBackend(TestCaseMemStorageBackend):

    def gen_new_filename(self, base='tmp_%s.db'):
        # f = base % uuid.uuid1()
        f = base % base64.b16encode(os.urandom(16))
        self.files.append(f)
        print("INFO: Generated new file: %s" % f)
        return f

    def setUp(self):
        self.files = []
        self.filename = self.gen_new_filename()
        self.s = FileStorageBackend(self.filename)

    def test_close(self):
        self.assertEqual(self.s.close(), None)

    def test_int_key(self):
        self.assertRaises(TypeError, self.s.set, 123, 'myval')

    def test_object_key(self):
        mykey = object()
        self.assertRaises(TypeError, self.s.set, mykey, 'myval')
        self.assertRaises(TypeError, self.s.set, mykey, 'myval2')
        self.assertRaises(TypeError, self.s.set, mykey, 'myval3')

    # def test_object_value(self):
    #     mykey = '234234'
    #     myval = object()
    #     self.assertRaises(TypeError, self.s.set, mykey, 'myval')
    #     self.assertRaises(TypeError, self.s.set, mykey, 'myval2')
    #     self.assertRaises(TypeError, self.s.set, mykey, 'myval3')


    @unittest.skip("bsddb adds .db to filename on mac.")
    def test_data_persistance(self):
        s = FileStorageBackend(self.filename, 'n')
        self.assertEqual(len(s), 0)
        s.set('mykeys', 'myvalues')
        self.assertEqual(len(s), 1)
        s = FileStorageBackend(self.filename, 'w')
        self.assertEqual(len(s), 1)
        self.assertEqual(s.get('mykeys'), 'myvalues')
        self.assertEqual(len(s), 1)
        del s['mykeys']
        self.assertEqual(len(s), 0)
        s.close()
        # shelve does not allow get on closed object
        self.assertRaises(ValueError, s.get, 'mykeys')
        s = FileStorageBackend(self.filename, 'w')
        self.assertRaises(KeyError, s.get, 'mykeys')
        self.assertEqual(len(s), 0)

    def tearDown(self):
        # Fixme: Should close config
        # self.s.close()
        # Delete all files which were created
        while len(self.files):
            f = self.files.pop()
            print("INFO: Deleting file: %s" % f)
            try:
                os.remove(f)
            except OSError:
                pass


class TestCaseConfigParserStorageBackend(TestCaseFileStorageBackend):

    def setUp(self):
        self.files = []
        self.filename = self.gen_new_filename()
        self.s = ConfigParserStorageBackend(self.filename)

    def test_object_key(self):
        mykey = object()
        self.assertRaises(AttributeError, self.s.set, mykey, 'myval')
        self.assertRaises(AttributeError, self.s.set, mykey, 'myval2')
        self.assertRaises(AttributeError, self.s.set, mykey, 'myval3')

    def test_int_key(self):
        self.assertRaises(AttributeError, self.s.set, 123, 'myval')

    def test_data_persistance_nosync_or_close(self):
        """test_data_persistance_nosync_or_close

        Using context to delete the object which will save the data to disk
        """
        # self.filename = self.gen_new_filename()

        def add_values():
            s = ConfigParserStorageBackend(self.filename)
            print("INFO: Items: %s" % str(s.store.items('DEFAULT')))
            print("INFO: Items: %s" % str(s.store.items('DEFAULT')))
            self.assertEqual(len(s), 0)
            s.set('mykeys', 'myvalues')
            s.set('mykeys2', 'myvalues')
            print("INFO: Items: %s" % str(s.store.items('DEFAULT')))
            self.assertEqual(len(s), 2)
        add_values()
        def open_again():
            s = ConfigParserStorageBackend(self.filename)
            print("INFO: Items: %s" % str(s.store.items('DEFAULT')))
            self.assertEqual(len(s), 2)
            self.assertEqual(s.get('mykeys'), 'myvalues')
            self.assertEqual(s.get('mykeys2'), 'myvalues')
            self.assertEqual(len(s), 2)
            del s['mykeys']
            self.assertEqual(len(s), 1)
        open_again()
        s = ConfigParserStorageBackend(self.filename)
        self.assertRaises(KeyError, s.get, 'mykeys')
        self.assertEqual(s.get('mykeys2'), 'myvalues')
        self.assertEqual(len(s), 1)

    def test_data_persistance_sync(self):
        # self.filename = self.gen_new_filename()
        s = ConfigParserStorageBackend(self.filename)
        print("INFO: Items: %s" % str(s.store.items('DEFAULT')))
        print("INFO: Items: %s" % str(s.store.items('DEFAULT')))
        self.assertEqual(len(s), 0)
        s.set('mykeys', 'myvalues')
        s.set('mykeys2', 'myvalues')
        print("INFO: Items: %s" % str(s.store.items('DEFAULT')))
        self.assertEqual(len(s), 2)
        s.sync()
        s = ConfigParserStorageBackend(self.filename)
        print("INFO: Items: %s" % str(s.store.items('DEFAULT')))
        self.assertEqual(len(s), 2)
        self.assertEqual(s.get('mykeys'), 'myvalues')
        self.assertEqual(s.get('mykeys2'), 'myvalues')
        self.assertEqual(len(s), 2)
        del s['mykeys']
        self.assertEqual(len(s), 1)
        s.close()
        s = ConfigParserStorageBackend(self.filename)
        self.assertRaises(KeyError, s.get, 'mykeys')
        self.assertEqual(s.get('mykeys2'), 'myvalues')
        self.assertEqual(len(s), 1)

    def test_data_persistance_with_close(self):
        # self.filename = self.gen_new_filename()
        s = ConfigParserStorageBackend(self.filename)
        print("INFO: Items: %s" % str(s.store.items('DEFAULT')))
        print("INFO: Items: %s" % str(s.store.items('DEFAULT')))
        self.assertEqual(len(s), 0)
        s.set('mykeys', 'myvalues')
        s.set('mykeys2', 'myvalues')
        print("INFO: Items: %s" % str(s.store.items('DEFAULT')))
        self.assertEqual(len(s), 2)
        s.close()
        s = ConfigParserStorageBackend(self.filename)
        print("INFO: Items: %s" % str(s.store.items('DEFAULT')))
        self.assertEqual(len(s), 2)
        self.assertEqual(s.get('mykeys'), 'myvalues')
        self.assertEqual(s.get('mykeys2'), 'myvalues')
        self.assertEqual(len(s), 2)
        del s['mykeys']
        self.assertEqual(len(s), 1)
        s.close()
        s = ConfigParserStorageBackend(self.filename)
        self.assertRaises(KeyError, s.get, 'mykeys')
        self.assertEqual(s.get('mykeys2'), 'myvalues')
        self.assertEqual(len(s), 1)


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


if __name__ == '__main__':
    print "INFO: Running tests!"
    unittest.main()

