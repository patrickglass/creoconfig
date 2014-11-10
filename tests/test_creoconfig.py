#!/usr/bin/env python
"""
Module test_creoconfig

UnitTest framework for validating CreoConfig
"""
import unittest
from creoconfig import Config
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
        self.assertRaises(KeyError, lambda: c['choice_key'])
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
        self.assertRaises(KeyError, lambda: c['choice_key'])
        self.assertTrue(c.prompt())
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


if __name__ == '__main__':
    print "INFO: Running tests!"
    unittest.main()

