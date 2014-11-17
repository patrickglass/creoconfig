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
from creoconfig.config import TimestampedConfig
from creoconfig.exceptions import *

import test_creoconfig

# class TestCaseTimestampedConfig(test_creoconfig.TestCaseConfig):
class TestCaseTimestampedConfig(unittest.TestCase):

    def setUp(self):
        self.cfg = TimestampedConfig

    # @patch('creoconfig.config.TimestampedConfig._timestamp', return_value=1400000000)
    # def test_timestamp_gen(self, input):
    #     c = self.cfg()
    #     self.assertEqual(c._timestamp(), input._mock_return_value)

    @patch('creoconfig.config.calendar.timegm', return_value=1400000000)
    def test_gen_value(self, input):
        c = self.cfg()
        val = 'myvalue'
        self.assertEqual(
            c._gen_value('myvalue'),
            "%s::%s" % (val, input._mock_return_value)
        )

    def test_gen_value_given(self):
        c = self.cfg()
        val = 'myvalue'
        self.assertEqual(
            c._gen_value('myvalue', 1400000000),
            "%s::%s" % (val, 1400000000)
        )

    def test_gen_value_given2(self):
        c = self.cfg()
        val = 'myvalue'
        self.assertEqual(
            c._gen_value('myvalue', 0),
            "%s::%s" % (val, 0)
        )

    def test_extract_value(self):
        c = self.cfg()
        val = 'myvalue::1400000001'
        self.assertEqual(c._extract_value(val), ('myvalue', 1400000001))

    @patch('creoconfig.config.calendar.timegm', return_value=1500000000)
    def test_gen_extract_value(self, input):
        c = self.cfg()
        val = c._gen_value('myvalue2')
        self.assertEqual(c._extract_value(val), ('myvalue2', 1500000000))

    # @patch('creoconfig.config.TimestampedConfig.calendar.timegm', return_value='100000')
    # def test_last_modified(self):
    #     self.cfg.set('myval', 'somevalue')
    #     self.cfg.last_mofified('myval')

    # @patch('creoconfig.config.TimestampedConfig.calendar.timegm', return_value='1000001')
    # def test_gen_value(self):
    #     c = self.cfg()
    #     self.assertEqual(c._gen_value('teststr'), 'teststr::100000')

