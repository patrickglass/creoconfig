#!/usr/bin/env python
"""
Module test_creoconfig

UnitTest framework for validating CreoConfig
"""
import unittest
from creoconfig import Config
from creoconfig.exceptions import *
from creoconfig.fields import *



# class TestCaseBasicInit(unittest.TestCase):

#     def test_no_token(self):
#         class myConfig(Config):
#             base_val = StringField()
#             base_val = StringField()

#         # self.assertEqual(myConfig.server, None)
#         # self.assertEqual(myConfig.cache_file, None)


# class TestCaseStringField(unittest.TestCase):

#     def test_valid_name(self):
#         """name of field must not be blank"""
#         self.assertTrue(StringField('testname'))

#     def test_invalid_name(self):
#         self.assertRaises(InvalidFieldName, StringField, '')
#         self.assertRaises(ConfigException, StringField, '')

#     def test_invalid_default(self):
#         """We have selected a default value that is not a valid option"""
#         self.assertRaises(InvalidFieldName, StringField, 'testname', 'e', ['a', 'b', 'c'])
#         self.assertRaises(ConfigException, StringField, 'testname', 'e', ['a', 'b', 'c'])

#     def test_complete_init(self):
#         f = StringField('testname', 'defval', ['a', 'b', 'c'], help_text="myhelp")
#         self.assertEqual(f.name, 'testname')
#         self.assertEqual(f.default, 'defval')
#         self.assertEqual(f.choices, ['a', 'b', 'c'])
#         self.assertEqual(f.validators, [])
#         self.assertEqual(f.help_text, "myhelp")

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
        c = Config()
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        self.assertRaises(AttributeError, c, 'mykey')
        self.assertRaises(KeyError, lambda: c['mykey'])

    def test_attr_del(self):
        c = Config()
        c.mykey = 'myvalue'
        self.assertEqual(c.mykey, 'myvalue')
        c._delete('mykey')
        # Second delete on non-existing key raises exception
        self.assertRaises(KeyError, c._delete, 'mykey')
        self.assertRaises(AttributeError, getattr, c, 'mykey')
        self.assertRaises(KeyError, lambda: c['mykey'])

    def test_sync_ok(self):
        c = Config()
        self.assertTrue(c.sync())


class TestWizardPrompt(unittest.TestCase):
    from mock import patch

    @patch('creoconfig.config.prompt_user', return_value='yes')
    def test_prompt_string(self, input):
        c = Config()
        c.add_option('strkey', help='This is a string key')
        c.prompt()

    @patch('creoconfig.config.prompt_user', return_value=123)
    def test_prompt_string(self, input):
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
        c.__setattr__('_batchmode', False, force=True)
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
        self.assertRaises(KeyError, lambda: c['choice_key'])
        self.assertTrue(c.prompt)
        print c.prompt()
        self.assertEqual(c.choice_key, 'ab')

    @patch('creoconfig.config.prompt_user', return_value='ab')
    def test_prompt_int_type_error(self, input):
        c = Config()
        c.add_option('choice_key',
            help='This is a int key which only allows certail values',
            type=int,
            choices=['a', 'abcd', 'ab', 'abc'])
        self.assertRaises(KeyError, lambda: c['choice_key'])
        self.assertTrue(c.prompt)
        print c.prompt()
        self.assertEqual(c.choice_key, 'ab')

    @patch('creoconfig.config.prompt_user', return_value='2')
    def test_prompt_int_choices_ok(self, input):
        c = Config()
        c.add_option('choice_key',
            help='This is a int key which only allows certail values',
            type=int,
            choices=[1, 2, 3, 10])
        self.assertRaises(KeyError, lambda: c['choice_key'])
        self.assertTrue(c.prompt())
        print c.prompt()
        self.assertEqual(c.choice_key, 2)


if __name__ == '__main__':
    print "INFO: Running tests!"
    unittest.main()

