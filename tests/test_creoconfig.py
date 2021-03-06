#!/usr/bin/env python
"""
Module test_creoconfig

UnitTest framework for validating CreoConfig
"""
try:
    import unittest2 as unittest
except:
    import unittest
import os
import base64
import unittest
from mock import patch
from creoconfig import Config
from creoconfig.storagebackend import (
    MemStorageBackend,
    XmlStorageBackend as FileStorageBackend,
    ConfigParserStorageBackend
)
from creoconfig.exceptions import *


class TestCaseConfig(unittest.TestCase):

    def setUp(self):
        self.cfg = Config

    @unittest.skip("values as dicts are not supported yet")
    def test_init(self):
        """
        Configs can start with initial values by passing in as extra args
        """
        c = self.cfg(defaults={'foo': 'bar', 'alpha': {'beta': 2, 'bravo': {}}})
        # as key
        self.assertEqual(c['foo'], 'bar')
        # as attribute
        self.assertEqual(c.foo, 'bar')
        # nested as key
        self.assertEqual(c['alpha'], {'beta': 2, 'bravo': {}})
        # nested as attribute
        self.assertEqual(c.alpha, {'beta': 2, 'bravo': {}})
        self.assertEqual(c.alpha.beta, 2)
        self.assertEqual(c.alpha.bravo, {})

    def test_supplied_default_dict(self):
        c = self.cfg(defaults={'foo': 'bar', 'alpha': 'beta', 'bravo': None})
        # as key
        self.assertEqual(c['foo'], 'bar')
        # as attribute
        self.assertEqual(c.foo, 'bar')
        # nested as key
        self.assertEqual(c['alpha'], 'beta')
        # nested as attribute
        self.assertEqual(c.alpha, 'beta')
        # FIXME: Configs always return things as strings.
        self.assertEqual(c.bravo, 'None')

    def test_options(self):
        c = self.cfg()
        c.add_option('strkey', help='This is a string key')
        c.add_option('intkey', help='This is a int key', type=int)
        c.add_option('choice_key',
            help='This is a int key which only allows certail values',
            type=int,
            choices=[1, 2, 3, 10])
        c.add_option('choice_key_str',
            help='This is a string key which only allows certail values',
            type=str,
            choices=['a', 'b', 'c', '10'])

    def test_get(self):
        """
        Test that attributes can be accessed (both as keys, and as
        attributes).
        """
        c = self.cfg(defaults={'foo': 'bar', 'mykey': 'myval'})
        print c.__dict__
        print c._store.store
        # found
        self.assertEqual(c.get('foo'), 'bar')
        # found, default given
        self.assertEqual(c.get('foo', 'baz'), 'bar')
        # not found
        self.assertRaises(KeyError, c.get, 'bar')
        # not found, default given
        self.assertEqual(c.get('bar', 'baz'), 'baz')

    def test_attr_set_get(self):
        c = self.cfg()
        c.mykey = 'myvalue'
        self.assertEqual(c.mykey, 'myvalue')
        c['mykey'] = 'myvalue2'
        self.assertEqual(c.mykey, 'myvalue2')
        c.mykey = 1234
        self.assertEqual(c['mykey'], '1234')

    def test_attr_set_alter_get(self):
        c = self.cfg()
        c.mykey = 'myvalue'
        c.mykey2 = 'myvalue2'
        c.mykey3 = 'myvalue3'
        c.mykey = 'resetvalue'
        self.assertEqual(c.mykey, 'resetvalue')
        self.assertEqual(c.mykey2, 'myvalue2')
        self.assertEqual(c.mykey3, 'myvalue3')
        c.mykey = 'myvalue2'
        self.assertEqual(c.mykey, 'myvalue2')
        c.mykey = 'myvalue3'
        self.assertEqual(c.mykey, 'myvalue3')
        c.mykey = 1234
        self.assertEqual(c['mykey'], '1234')


    def test_dict_set_alter_get(self):
        c = self.cfg()
        c['mykey'] = 'myvalue'
        self.assertEqual(c['mykey'], 'myvalue')
        c['mykey'] = 'myvalue2'
        self.assertEqual(c['mykey'], 'myvalue2')
        c['mykey'] = 'myvalue3'
        self.assertEqual(c['mykey'], 'myvalue3')
        c['mykey'] = 1234
        self.assertEqual(c['mykey'], '1234')

    def test_dict_attr_set_alter_get(self):
        c = self.cfg()
        c['mykey'] = 'myvalue'
        self.assertEqual(c['mykey'], 'myvalue')
        c.mykey = 'myvalue2'
        self.assertEqual(c.mykey, 'myvalue2')
        c['mykey'] = 'myvalue3'
        self.assertEqual(c['mykey'], 'myvalue3')
        c.mykey = 1234
        self.assertEqual(c['mykey'], '1234')

    def test_attr_missing(self):
        c = self.cfg(batch=True)
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        # Users the class __call__ method
        # self.assertRaises(AttributeError, c, 'mykey')
        self.assertRaises(KeyError, lambda: c['mykey'])

    def test_delete_func(self):
        c = self.cfg(batch=True)
        c.mykey = 'myvalue'
        self.assertEqual(c.mykey, 'myvalue')
        delattr(c, 'mykey')
        # Second delete on non-existing key raises exception
        self.assertRaises(AttributeError, delattr, c, 'mykey')
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        self.assertRaises(KeyError, lambda: c['mykey'])

    def test_delete_func2(self):
        c = self.cfg(batch=True)
        c.mykey = 'myvalue'
        self.assertEqual(c.mykey, 'myvalue')
        del c.mykey
        # Second delete on non-existing key raises exception
        self.assertRaises(AttributeError, delattr, c, 'mykey')
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        self.assertRaises(KeyError, lambda: c['mykey'])

    def test_delete_dict(self):
        c = self.cfg(batch=True)
        c.mykey = 'myvalue'
        self.assertEqual(c.mykey, 'myvalue')
        del c['mykey']
        # Second delete on non-existing key raises exception
        self.assertRaises(AttributeError, delattr, c, 'mykey')
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        self.assertRaises(KeyError, lambda: c['mykey'])

    def test_delete_attr(self):
        c = self.cfg(batch=True)
        c.mykey = 'myvalue'
        self.assertEqual(c.mykey, 'myvalue')
        del c.mykey
        # Second delete on non-existing key raises exception
        self.assertRaises(AttributeError, delattr, c, 'mykey')
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        self.assertRaises(KeyError, lambda: c['mykey'])

    def test_batch_enable(self):
        """test_batch_enable - ensure we can enable batchmode if not set"""
        c = self.cfg()
        print c.__dict__
        print c._store.__dict__
        self.assertFalse(c._isbatch)
        c.enable_batch()
        print c.__dict__
        print c._store.__dict__
        self.assertTrue(c._isbatch)

    def test_batch_disable(self):
        """test_batch_disable - ensure we can disable batchmode if set"""
        c = self.cfg(batch=True)
        self.assertTrue(c._isbatch)
        c.disable_batch()
        self.assertFalse(c._isbatch)

    def test_erase_all(self):
        c = self.cfg()
        c.mykey = 'myvalue'
        c.mykey2 = 'myvalue2'
        c.mykey3 = 'myvalue3'
        c.mykey = 'resetvalue'
        self.assertEqual(c.mykey, 'resetvalue')
        self.assertEqual(c.mykey2, 'myvalue2')
        self.assertEqual(c.mykey3, 'myvalue3')
        self.assertEqual(len(c), 3)
        # Delete all the items
        for x in c.keys():
            del c[x]
        self.assertEqual(len(c), 0)
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        c.testkey = 'avalue'
        self.assertEqual(c.testkey, 'avalue')
        self.assertEqual(len(c), 1)

    def test_len(self):
        c = self.cfg()
        self.assertEqual(len(c), 0)
        c.mykey = 'myvalue'
        self.assertEqual(len(c), 1)
        c.mykey2 = 'myvalue2'
        self.assertEqual(len(c), 2)
        c.mykey3 = 'myvalue3'
        self.assertEqual(len(c), 3)
        c.mykey = 'resetvalue'
        self.assertEqual(len(c), 3)
        del c.mykey
        self.assertEqual(len(c), 2)
        c.mykey = 1243
        self.assertEqual(len(c), 3)
        # Delete all the items
        for x in c.keys():
            print "INFO: Deleting %s" % x
            del c[x]
        self.assertEqual(len(c), 0)


# class TestWizardPrompt(unittest.TestCase):

#     def setUp(self):
#         """Set the class to use for all testcases"""
#         self.cfg = Config

    @patch('__builtin__.raw_input', return_value='yes')
    def test_prompt_string(self, input):
        c = self.cfg()
        c.add_option('strkey', help='This is a string key')
        c.prompt()

    @patch('__builtin__.raw_input', return_value=123)
    def test_prompt_int(self, input):
        c = self.cfg()
        c.add_option('intkey', type=int)
        c.prompt()

    def test_prompt_batchmode_enabled(self):
        c = self.cfg(batch=True)
        c.add_option('intkey', type=int)
        self.assertRaises(BatchModeUnableToPrompt, lambda: c.prompt())
        self.assertRaises(BatchModeUnableToPrompt, lambda: c.prompt())

    def test_prompt_batchmode_enabled_with_default(self):
        c = self.cfg(batch=True)
        c.add_option('keyname', type=str, default='someval')
        self.assertEqual(c.keyname, 'someval')

    @patch('__builtin__.raw_input', return_value='abc')
    def test_prompt_batchmode_enabled_disabled(self, input):
        c = self.cfg(batch=True)
        c.add_option('strkey', help='This is a string key')
        self.assertRaises(BatchModeUnableToPrompt, lambda: c.prompt())
        self.assertRaises(BatchModeUnableToPrompt, lambda: c.prompt())
        self.assertRaises(KeyError, lambda: c['strkey'])
        c.disable_batch()
        print "BatchMode: %s" % c._isbatch
        print "options: %s" % c._available_keywords
        self.assertTrue(c.prompt())
        self.assertEquals(c.strkey, 'abc')

    @patch('__builtin__.raw_input', return_value=123)
    def test_prompt_int_choices_bad(self, input):
        c = self.cfg()
        c.add_option('choice_key',
            help='This is a int key which only allows certail values',
            type=int,
            choices=[1, 2, 3, 10])
        self.assertRaises(TooManyRetries, lambda: c.prompt())

    @patch('__builtin__.raw_input', return_value='123')
    def test_prompt_string_choices_bad(self, input):
        c = self.cfg()
        c.add_option('choice_key',
            help='This is a int key which only allows certail values',
            type=str,
            choices=['1', '2', '3', '10'])
        self.assertRaises(TooManyRetries, lambda: c.prompt())

    @patch('__builtin__.raw_input', return_value='ab')
    def test_prompt_string_choices_ok(self, input):
        c = self.cfg()
        c.add_option('choice_key',
            help='This is a int key which only allows certail values',
            type=str,
            choices=['a', 'abcd', 'ab', 'abc'])
        self.assertEqual(c['choice_key'], 'ab')
        self.assertTrue(c.prompt())
        self.assertEqual(c.choice_key, 'ab')

    @patch('__builtin__.raw_input', return_value='ab')
    def test_prompt_int_type_error(self, input):
        c = self.cfg()
        self.assertRaises(IllegalArgumentError,
            c.add_option,
            'choice_key',
            help='This is a int key which only allows certail values',
            type=int,
            choices=[1, 'string', 'a', 'abcd', 'ab', 'abc'])

    @patch('__builtin__.raw_input', return_value='2')
    def test_prompt_int_choices_ok(self, input):
        c = self.cfg()
        c.add_option('choice_key',
            help='This is a int key which only allows certail values',
            type=int,
            choices=[1, 2, 3, 10])
        # Since we have autoprompting this is no longer relavant
        # self.assertRaises(KeyError, lambda: c['choice_key'])
        # self.assertTrue(c.prompt())
        self.assertEqual(c.choice_key, 2)

    @patch('__builtin__.raw_input', return_value='ab')
    def test_prompt_int_cast_failure(self, input):
        c = self.cfg()
        c.add_option('keyname', type=int)
        self.assertRaises(TooManyRetries, lambda: c['keyname'])

    @patch('__builtin__.raw_input', return_value='')
    def test_prompt_empty_ans_no_default(self, input):
        c = self.cfg()
        c.add_option('keyname', type=int)
        self.assertRaises(TooManyRetries, lambda: c['keyname'])

    @patch('__builtin__.raw_input', return_value='')
    def test_prompt_empty_ans_print_help(self, input):
        c = self.cfg()
        c.add_option('keyname', type=int, help='help string here')
        self.assertRaises(TooManyRetries, lambda: c['keyname'])


# class TestConfigOptionDefault(unittest.TestCase):

#     def setUp(self):
#         """Set the class to use for all testcases"""
#         self.cfg = Config

    def test_default_type_match_int(self):
        c = self.cfg()
        self.assertTrue(c.add_option('keyname', type=int, default=234))
        # self.assertEqual(c.keyname, '234')

    def test_default_type_mismatch_int(self):
        c = self.cfg()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=int, default='32')
        # self.assertEqual(c.keyname, '32')

    def test_default_type_mismatch_int2(self):
        c = self.cfg()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=int, default=354.545)
        # self.assertEqual(c.keyname, '354.545')

    def test_default_type_match_float(self):
        c = self.cfg()
        self.assertTrue(c.add_option('keyname', type=float, default=0.0))
        # self.assertEqual(c.keyname, '0.0')

    def test_default_type_mismatch_float(self):
        c = self.cfg()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=float, default='354.545')
        # self.assertEqual(c.keyname, '354.545')

    def test_default_type_mismatch_float2(self):
        c = self.cfg()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=float, default=354)
        # self.assertEqual(c.keyname, '354')

    def test_default_type_match_str(self):
        c = self.cfg()
        self.assertTrue(c.add_option('keyname', type=str, default='234'))
        # self.assertEqual(c.keyname, '234')

    def test_default_type_match_str2(self):
        c = self.cfg()
        self.assertTrue(c.add_option('keyname', type=str, default=' spaces everywhere   '))
        # self.assertEqual(c.keyname, ' spaces everywhere   ')

    def test_default_type_mismatch_str(self):
        c = self.cfg()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=str, default=354.545)
        # self.assertEqual(c.keyname, '354.545')


# class TestConfigBackendOverride(unittest.TestCase):

#     def setUp(self):
#         """Set the class to use for all testcases"""
#         self.cfg = Config

    def test_mem(self):
        c = self.cfg()
        self.assertIsInstance(c._store, MemStorageBackend)

# class TestConfigOptionChoices(unittest.TestCase):

#     def setUp(self):
#         """Set the class to use for all testcases"""
#         self.cfg = Config

    def test_choice_type_match_int(self):
        c = self.cfg()
        self.assertTrue(c.add_option('keyname', type=int, choices=[234, 1]))

    def test_choice_type_match_single_int(self):
        c = self.cfg()
        self.assertRaises(TypeError, c.add_option, 'keyname', type=int, choices=234)

    def test_choice_type_mismatch_int(self):
        c = self.cfg()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=int, choices=['32', 'asb'])

    def test_choice_type_mismatch_int2(self):
        c = self.cfg()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=int, choices=[354.545])

    def test_choice_type_match_float(self):
        c = self.cfg()
        self.assertTrue(c.add_option('keyname', type=float, choices=[0.0]))

    def test_choice_type_match_single_float(self):
        c = self.cfg()
        self.assertRaises(TypeError, c.add_option, 'keyname', type=float, choices=234.0)

    def test_choice_type_mismatch_float(self):
        c = self.cfg()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=float, choices=['354.545'])

    def test_choice_type_mismatch_float2(self):
        c = self.cfg()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=float, choices=[354])

    def test_choice_type_match_single_string(self):
        c = self.cfg()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=str, choices="BadChoice")

    def test_choice_type_match_str(self):
        c = self.cfg()
        self.assertTrue(c.add_option('keyname', type=str, choices=['234']))

    def test_choice_type_match_str2(self):
        c = self.cfg()
        self.assertTrue(c.add_option('keyname', type=str, choices=[' spaces everywhere   ']))

    def test_choice_type_mismatch_str(self):
        c = self.cfg()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=str, choices=[354.545])


# class TestConfigOptionAutoPrompt(unittest.TestCase):

#     def setUp(self):
#         self.cfg = Config

    @patch('__builtin__.raw_input', return_value='2')
    def test_prompt_int_dict_default(self, input):
        c = self.cfg()
        c.add_option('choice_key',
            type=int,
            default=2)
        self.assertEqual(c['choice_key'], 2)

    @patch('__builtin__.raw_input', return_value='2')
    def test_prompt_int_attr_default(self, input):
        c = self.cfg()
        c.add_option('choice_key',
            type=int,
            default=2)
        self.assertEqual(c.choice_key, 2)

    @patch('__builtin__.raw_input', return_value='2')
    def test_prompt_int_dict_no_default(self, input):
        c = self.cfg()
        c.add_option('choice_key',
            type=int)
        self.assertEqual(c['choice_key'], 2)

    @patch('__builtin__.raw_input', return_value='2')
    def test_prompt_int_attr_no_default(self, input):
        c = self.cfg()
        c.add_option('choice_key',
            type=int)
        self.assertEqual(c.choice_key, 2)

    @patch('__builtin__.raw_input', return_value='2')
    def test_prompt_int_dict_batch_no_default(self, input):
        c = self.cfg(batch=True)
        c.add_option('choice_key',
            type=int)
        self.assertRaises(KeyError, lambda: c['mykey'])

    @patch('__builtin__.raw_input', return_value='2')
    def test_prompt_int_attr_batch_no_default(self, input):
        c = self.cfg(batch=True)
        c.add_option('choice_key',
            type=int)
        self.assertRaises(AttributeError, getattr, c, 'mykey')


class TestConfigFileBackend(unittest.TestCase):

    def setUp(self):
        """Set the class to use for all testcases"""
        self.cfg = Config
        self.files = []

    def gen_new_filename(self, base='tmp_%s.cfg'):
        # f = base % uuid.uuid1()
        f = base % base64.b16encode(os.urandom(16))
        self.files.append(f)
        print("INFO: Generated new file: %s" % f)
        return f

    def test_file(self):
        c = self.cfg(filename=self.gen_new_filename())
        self.assertIsInstance(c._store, FileStorageBackend)

    def test_file_def_order(self):
        c = self.cfg(self.gen_new_filename())
        self.assertIsInstance(c._store, FileStorageBackend)

    def test_file_persistance_overwrite_var(self):
        f = self.gen_new_filename()
        c = self.cfg(f)
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        c.mykey = 'myvalue'
        c.keytodelete = 'secretvalue'
        c.anotherkey = 'someothervalue'
        c['dictkey'] = 'values'
        print c['mykey']
        print c._store.__dict__
        self.assertEqual(c.dictkey, 'values')
        self.assertEqual(c.mykey, 'myvalue')
        self.assertEqual(c.keytodelete, 'secretvalue')
        self.assertEqual(c.anotherkey, 'someothervalue')

        # Now recreate the Config and check if value is taken
        # we dont want to auto create file if it does not exists.
        c = self.cfg(f)
        print c._store.__dict__
        self.assertEqual(c.dictkey, 'values')
        self.assertEqual(c.mykey, 'myvalue')
        self.assertEqual(c.keytodelete, 'secretvalue')
        self.assertEqual(c.anotherkey, 'someothervalue')
        del c.keytodelete
        print c['mykey']
        del c['mykey']
        self.assertRaises(KeyError, lambda: c['mykey'])
        self.assertRaises(KeyError, lambda: c['keytodelete'])
        self.assertEqual(c.anotherkey, 'someothervalue')
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        self.assertRaises(KeyError, lambda: c['mykey'])

    def test_file_persistance_context(self):
        f = self.gen_new_filename()
        def create_data():
            c = self.cfg(f)
            self.assertRaises(AttributeError, getattr, c, 'mykey')
            c.mykey = 'myvalue'
            c.keytodelete = 'secretvalue'
            c.anotherkey = 'someothervalue'
            print c['mykey']
            print c._store.__dict__
            self.assertEqual(c.mykey, 'myvalue')
            self.assertEqual(c.keytodelete, 'secretvalue')
            self.assertEqual(c.anotherkey, 'someothervalue')
        create_data()
        # Now recreate the Config and check if value is taken
        c = self.cfg(f)
        print c._store.__dict__
        print c['mykey']
        self.assertEqual(c.mykey, 'myvalue')
        self.assertEqual(c.keytodelete, 'secretvalue')
        self.assertEqual(c.anotherkey, 'someothervalue')
        del c.keytodelete
        print c['mykey']
        print c._store.__dict__
        delattr(c, 'mykey')
        # del c['mykey']
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        self.assertRaises(KeyError, lambda: c['mykey'])

    def test_file_persistance_with_close(self):
        f = self.gen_new_filename()
        c = self.cfg(f)
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        c.mykey = 'myvalue'
        c.keytodelete = 'secretvalue'
        c.anotherkey = 'someothervalue'
        c['dictkey'] = 'values'
        print c['mykey']
        print c._store.__dict__
        self.assertEqual(c.dictkey, 'values')
        self.assertEqual(c.mykey, 'myvalue')
        self.assertEqual(c.keytodelete, 'secretvalue')
        self.assertEqual(c.anotherkey, 'someothervalue')

        # Now recreate the Config and check if value is taken
        # we dont want to auto create file if it does not exists.
        c = self.cfg(f)
        print c._store.__dict__
        self.assertEqual(c.dictkey, 'values')
        self.assertEqual(c.mykey, 'myvalue')
        self.assertEqual(c.keytodelete, 'secretvalue')
        self.assertEqual(c.anotherkey, 'someothervalue')
        # FIXME: Why does this del not work (TypeError: Invalid key: 'mykey')
        del c.keytodelete
        print c['mykey']
        del c['mykey']
        # self.assertEqual(c.mykey, 'myvalue')
        self.assertRaises(KeyError, lambda: c['mykey'])
        self.assertRaises(KeyError, lambda: c['keytodelete'])
        self.assertEqual(c.anotherkey, 'someothervalue')
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        self.assertRaises(KeyError, lambda: c['mykey'])

        # Lets create a new config one more time
        c = self.cfg(f)
        print c._store.__dict__
        self.assertEqual(c.dictkey, 'values')
        self.assertEqual(c.anotherkey, 'someothervalue')

        # Lets create a new config one more time
        c = self.cfg(f)
        print c._store.__dict__
        self.assertEqual(c.dictkey, 'values')
        self.assertEqual(c.anotherkey, 'someothervalue')


    #
    # Test last_modified method
    #
    @patch('creoconfig.storagebackend.time.time', return_value=1300000001)
    def test_last_modified_mem(self, input):
        c = self.cfg()
        c.testkey = 'somevalue'
        self.assertEqual(c.testkey, 'somevalue')
        # MemoryStorageBackend does not support extra kvp attributes
        self.assertEqual(c.last_modified('testkey'), None)

    @patch('creoconfig.storagebackend.time.time', return_value=1300000001)
    def test_last_modified_xml(self, input):
        c = self.cfg(self.gen_new_filename())
        c.testkey = 'somevalue'
        self.assertEqual(c.testkey, 'somevalue')
        self.assertEqual(c.last_modified('testkey'), input._mock_return_value)

    # @unittest.skip("these test since this config only returns strings")
    # def test_prompt_int_choices_ok(self):
    #     pass

    # @unittest.skip("these test since this config only returns strings")
    # def test_prompt_int_dict_default(self):
    #     pass

    # @unittest.skip("these test since this config only returns strings")
    # def test_prompt_int_dict_no_default(self):
    #     pass

    # @unittest.skip("these test since this config only returns strings")
    # def test_prompt_int_attr_no_default(self):
    #     pass

    # @unittest.skip("these test since this config only returns strings")
    # def test_prompt_int_attr_default(self):
    #     pass

    def tearDown(self):
        # Delete all files which were created
        while len(self.files):
            f = self.files.pop()
            print("INFO: Deleting file: %s" % f)
            try:
                os.remove(f)
            except OSError:
                pass


if __name__ == '__main__':
    print "INFO: Running tests!"
    unittest.main()

