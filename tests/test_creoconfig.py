#!/usr/bin/env python
"""
Module test_creoconfig

UnitTest framework for validating CreoConfig
"""
import unittest
from mock import patch
from creoconfig import Config, FileStorageBackend
from creoconfig.exceptions import *


class TestCaseConfig(unittest.TestCase):

    def test_options(self):
        c = Config()
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

    def test_attr_set_get(self):
        c = Config()
        c.mykey = 'myvalue'
        self.assertEqual(c.mykey, 'myvalue')
        c['mykey'] = 'myvalue2'
        self.assertEqual(c.mykey, 'myvalue2')
        c.mykey = 1234
        self.assertEqual(c['mykey'], 1234)

    def test_attr_missing(self):
        c = Config(batch=True)
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        self.assertRaises(AttributeError, c, 'mykey')
        self.assertRaises(KeyError, lambda: c['mykey'])

    def test_delete_func(self):
        c = Config(batch=True)
        c.mykey = 'myvalue'
        self.assertEqual(c.mykey, 'myvalue')
        delattr(c, 'mykey')
        # Second delete on non-existing key raises exception
        self.assertRaises(TypeError, delattr, c, 'mykey')
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        self.assertRaises(KeyError, lambda: c['mykey'])

    def test_delete_func2(self):
        c = Config(batch=True)
        c.mykey = 'myvalue'
        self.assertEqual(c.mykey, 'myvalue')
        del c.mykey
        # Second delete on non-existing key raises exception
        self.assertRaises(TypeError, delattr, c, 'mykey')
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        self.assertRaises(KeyError, lambda: c['mykey'])

    def test_delete_dict(self):
        c = Config(batch=True)
        c.mykey = 'myvalue'
        self.assertEqual(c.mykey, 'myvalue')
        del c['mykey']
        # Second delete on non-existing key raises exception
        self.assertRaises(TypeError, delattr, c, 'mykey')
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        self.assertRaises(KeyError, lambda: c['mykey'])

    def test_delete_attr(self):
        c = Config(batch=True)
        c.mykey = 'myvalue'
        self.assertEqual(c.mykey, 'myvalue')
        del c.mykey
        # Second delete on non-existing key raises exception
        self.assertRaises(TypeError, delattr, c, 'mykey')
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        self.assertRaises(KeyError, lambda: c['mykey'])

    def test_sync_ok(self):
        """Config.sync() should not throw an error"""
        c = Config()
        c.sync()


class TestWizardPrompt(unittest.TestCase):

    @patch('creoconfig.config.prompt_user', return_value='yes')
    def test_prompt_string(self, input):
        c = Config()
        c.add_option('strkey', help='This is a string key')
        c.prompt()

    @patch('creoconfig.config.prompt_user', return_value=123)
    def test_prompt_int(self, input):
        c = Config()
        c.add_option('intkey', help='This is a int key', type=int)
        c.prompt()

    def test_prompt_batchmode_enabled(self):
        c = Config(batch=True)
        c.add_option('intkey', help='This is a int key', type=int)
        self.assertRaises(BatchModeUnableToPromt, lambda: c.prompt())
        self.assertRaises(BatchModeUnableToPromt, lambda: c.prompt())

    @patch('creoconfig.config.prompt_user', return_value='abc')
    def test_prompt_batchmode_enabled_disabled(self, input):
        c = Config(batch=True)
        c.add_option('strkey', help='This is a string key')
        self.assertRaises(BatchModeUnableToPromt, lambda: c.prompt())
        self.assertRaises(BatchModeUnableToPromt, lambda: c.prompt())
        self.assertRaises(KeyError, lambda: c['strkey'])
        c._meta.batchmode = False
        self.assertTrue(c.prompt())
        self.assertEquals(c.strkey, 'abc')

    @patch('creoconfig.config.prompt_user', return_value=123)
    def test_prompt_int_choices_bad(self, input):
        c = Config()
        c.add_option('choice_key',
            help='This is a int key which only allows certail values',
            type=int,
            choices=[1, 2, 3, 10])
        self.assertRaises(TooManyRetries, lambda: c.prompt())

    @patch('creoconfig.config.prompt_user', return_value='123')
    def test_prompt_string_choices_bad(self, input):
        c = Config()
        c.add_option('choice_key',
            help='This is a int key which only allows certail values',
            type=str,
            choices=['1', '2', '3', '10'])
        self.assertRaises(TooManyRetries, lambda: c.prompt())

    @patch('creoconfig.config.prompt_user', return_value='ab')
    def test_prompt_string_choices_ok(self, input):
        c = Config()
        c.add_option('choice_key',
            help='This is a int key which only allows certail values',
            type=str,
            choices=['a', 'abcd', 'ab', 'abc'])
        self.assertEqual(c['choice_key'], 'ab')
        self.assertTrue(c.prompt())
        self.assertEqual(c.choice_key, 'ab')

    @patch('creoconfig.config.prompt_user', return_value='ab')
    def test_prompt_int_type_error(self, input):
        c = Config()
        self.assertRaises(IllegalArgumentError,
            c.add_option,
            'choice_key',
            help='This is a int key which only allows certail values',
            type=int,
            choices=[1, 'string', 'a', 'abcd', 'ab', 'abc'])

    @patch('creoconfig.config.prompt_user', return_value='2')
    def test_prompt_int_choices_ok(self, input):
        c = Config()
        c.add_option('choice_key',
            help='This is a int key which only allows certail values',
            type=int,
            choices=[1, 2, 3, 10])
        # Since we have autoprompting this is no longer relavant
        # self.assertRaises(KeyError, lambda: c['choice_key'])
        # self.assertTrue(c.prompt())
        self.assertEqual(c.choice_key, 2)


class TestConfigOptionDefault(unittest.TestCase):

    def test_default_type_match_int(self):
        c = Config()
        self.assertTrue(c.add_option('keyname', type=int, default=234))

    def test_default_type_mismatch_int(self):
        c = Config()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=int, default='32')

    def test_default_type_mismatch_int2(self):
        c = Config()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=int, default=354.545)

    def test_default_type_match_float(self):
        c = Config()
        self.assertTrue(c.add_option('keyname', type=float, default=0.0))

    def test_default_type_mismatch_float(self):
        c = Config()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=float, default='354.545')

    def test_default_type_mismatch_float2(self):
        c = Config()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=float, default=354)

    def test_default_type_match_str(self):
        c = Config()
        self.assertTrue(c.add_option('keyname', type=str, default='234'))

    def test_default_type_match_str2(self):
        c = Config()
        self.assertTrue(c.add_option('keyname', type=str, default=' spaces everywhere   '))

    def test_default_type_mismatch_str(self):
        c = Config()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=str, default=354.545)


class TestConfigOptionChoices(unittest.TestCase):

    def test_choice_type_match_int(self):
        c = Config()
        self.assertTrue(c.add_option('keyname', type=int, choices=[234, 1]))

    def test_choice_type_match_single_int(self):
        c = Config()
        self.assertRaises(TypeError, c.add_option, 'keyname', type=int, choices=234)

    def test_choice_type_mismatch_int(self):
        c = Config()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=int, choices=['32', 'asb'])

    def test_choice_type_mismatch_int2(self):
        c = Config()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=int, choices=[354.545])

    def test_choice_type_match_float(self):
        c = Config()
        self.assertTrue(c.add_option('keyname', type=float, choices=[0.0]))

    def test_choice_type_match_single_float(self):
        c = Config()
        self.assertRaises(TypeError, c.add_option, 'keyname', type=float, choices=234.0)

    def test_choice_type_mismatch_float(self):
        c = Config()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=float, choices=['354.545'])

    def test_choice_type_mismatch_float2(self):
        c = Config()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=float, choices=[354])

    def test_choice_type_match_single_string(self):
        c = Config()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=str, choices="BadChoice")

    def test_choice_type_match_str(self):
        c = Config()
        self.assertTrue(c.add_option('keyname', type=str, choices=['234']))

    def test_choice_type_match_str2(self):
        c = Config()
        self.assertTrue(c.add_option('keyname', type=str, choices=[' spaces everywhere   ']))

    def test_choice_type_mismatch_str(self):
        c = Config()
        self.assertRaises(IllegalArgumentError, c.add_option, 'keyname', type=str, choices=[354.545])


class TestConfigOptionAutoPrompt(unittest.TestCase):

    @patch('creoconfig.config.prompt_user', return_value='2')
    def test_prompt_int_dict_default(self, input):
        c = Config()
        c.add_option('choice_key',
            type=int,
            default=2)
        self.assertEqual(c['choice_key'], 2)

    @patch('creoconfig.config.prompt_user', return_value='2')
    def test_prompt_int_attr_default(self, input):
        c = Config()
        c.add_option('choice_key',
            type=int,
            default=2)
        self.assertEqual(c.choice_key, 2)

    @patch('creoconfig.config.prompt_user', return_value='2')
    def test_prompt_int_dict_no_default(self, input):
        c = Config()
        c.add_option('choice_key',
            type=int)
        self.assertEqual(c['choice_key'], 2)

    @patch('creoconfig.config.prompt_user', return_value='2')
    def test_prompt_int_attr_no_default(self, input):
        c = Config()
        c.add_option('choice_key',
            type=int)
        self.assertEqual(c.choice_key, 2)

    @patch('creoconfig.config.prompt_user', return_value='2')
    def test_prompt_int_dict_batch_no_default(self, input):
        c = Config(batch=True)
        c.add_option('choice_key',
            type=int)
        self.assertRaises(KeyError, lambda: c['mykey'])

    @patch('creoconfig.config.prompt_user', return_value='2')
    def test_prompt_int_attr_batch_no_default(self, input):
        c = Config(batch=True)
        c.add_option('choice_key',
            type=int)
        self.assertRaises(AttributeError, c, 'mykey')


class TestConfigFileBackend(unittest.TestCase):

    def setUp(self):
        self.filename = 'tmp_TestConfigFileBackend.cfg'
    #     self.backend = FileStorageBackend(filename=self.filename)
    #     self.c = Config(batch=True, backend=self.backend)

    # def test_create_mykey(self):
    #     self.c.mykey = 'myvalue'

    # def test_get_mykey(self):
    #     self.assertEqual(self.c.mykey, 'myvalue')

    def test_sync_ok(self):
        """Config.sync() should not throw an exception"""
        s = FileStorageBackend(self.filename)
        c = Config(backend=s)
        c.sync()

    @unittest.skip("Not working since backend does not populate mapping")
    def test_file_persistance(self):
        c = Config(backend=FileStorageBackend(self.filename))
        self.assertRaises(AttributeError, c, 'mykey')
        c.mykey = 'myvalue'
        c.anotherkey = 'someothervalue'
        print c['mykey']
        print c.__dict__
        print c._meta.backend.__dict__
        print c._mapping
        self.assertEqual(c.mykey, 'myvalue')

        # Now recreate the Config and check if value is taken
        c = Config(backend=FileStorageBackend(self.filename))
        self.assertEqual(c.mykey, 'myvalue')
        # FIXME: Why does this del not work (TypeError: Invalid key: 'mykey')
        # del c.mykey
        print c['mykey']
        print c.__dict__
        print c._meta.backend.__dict__
        print c._mapping
        delattr(c, 'mykey')
        # del c['mykey']
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        self.assertRaises(KeyError, lambda: c['mykey'])

    @unittest.skip("Not working since backend does not populate mapping")
    def test_file_persistance_with_close(self):
        c = Config(backend=FileStorageBackend(self.filename))
        self.assertRaises(AttributeError, c, 'mykey')
        c.mykey = 'myvalue'
        self.assertEqual(c.mykey, 'myvalue')

        # Close should be optional, since orphaning original c
        # should auto close the backend
        c.close()

        # Now recreate the Config and check if value is taken
        c = Config(backend=FileStorageBackend(self.filename))
        self.assertEqual(c.mykey, 'myvalue')
        # FIXME: Why does this del not work (TypeError: Invalid key: 'mykey')
        # del c.mykey
        print c['mykey']
        del c['mykey']
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        self.assertRaises(KeyError, lambda: c['mykey'])

    # def tearDown(self):
    #     self.backend.close()
    #     del self.s
    #     try:
    #         os.remove(self.filename)
    #     except:
    #         pass
    #     try:
    #         os.remove(self.filename + '.db')
    #     except:
    #         pass



if __name__ == '__main__':
    print "INFO: Running tests!"
    unittest.main()

