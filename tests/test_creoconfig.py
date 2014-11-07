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

    def test_sync_ok(self):
        c = Config()
        self.assertTrue(c.sync())

if __name__ == '__main__':
    print "INFO: Running tests!"
    unittest.main()

