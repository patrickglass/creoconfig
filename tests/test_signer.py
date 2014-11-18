#!/usr/bin/env python
"""
Module test_signing
"""
try:
    import unittest2 as unittest
except:
    import unittest
import os
import base64
import unittest
from creoconfig.signing import *
from creoconfig.exceptions import *


class TestCaseBaseSigner(unittest.TestCase):

    def setUp(self):
        self.cls = Signer

    def test_init(self):
        s = self.cls()
        s = self.cls('secretkey', 'specialsalt')
        s = self.cls(key='secretkey', salt='specialsalt')


    def test_sign_unsign(self):
        s = self.cls()
        val = 'myvalue'
        enc = s.sign(val)
        print("INFO: Encoded %s -> %s" % (val, enc))
        dec = s.unsign(enc)
        print("INFO: Decoded %s -> %s" % (enc, dec))
        self.assertEqual(val, dec)


class TestCaseTimestampSigner(TestCaseBaseSigner):

    def setUp(self):
        self.cls = TimestampSigner

    def test_sign_unsign(self):
        s = self.cls()
        val = 'myvalue'
        enc = s.sign(val)
        print("INFO: Encoded %s -> %s" % (val, enc))
        (dec, t) = s.unsign(enc)
        print("INFO: Decoded %s -> %s" % (enc, dec))
        self.assertEqual(val, dec)
