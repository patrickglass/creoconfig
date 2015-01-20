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


def _alter_str(data, pos=0, incr=1, num=1):
    """Alters a string at the given position by incrementing the char"""
    start = pos
    assert pos >= 0
    assert incr >= 0
    assert num >= 0
    assert len(data) >= (pos + num)
    while pos < num + start:
        data = data[:pos] + chr(ord(data[pos]) + incr) + data[pos+1:]
        pos += 1
    return data

class TestCaseBaseSigner(unittest.TestCase):

    def setUp(self):
        self.cls = Signer

    def test_alter_str(self):
        s = 'abcde'
        self.assertEqual(_alter_str(s, incr=0), 'abcde')
        self.assertEqual(_alter_str(s, num=0), 'abcde')
        self.assertEqual(_alter_str(s), 'bbcde')
        self.assertEqual(_alter_str(s, 0), 'bbcde')
        self.assertEqual(_alter_str(s, 1), 'accde')
        self.assertEqual(_alter_str(s, 2), 'abdde')
        self.assertEqual(_alter_str(s, 3), 'abcee')
        self.assertEqual(_alter_str(s, 4), 'abcdf')
        self.assertRaises(AssertionError, _alter_str, s, 5)

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

    def test_sign_unsign_str(self):
        s = self.cls()
        val = 'myvalue'
        enc = str(s.sign(val))
        print("INFO: Encoded %s -> %s" % (val, enc))
        dec = s.unsign(enc)
        print("INFO: Decoded %s -> %s" % (enc, dec))
        self.assertEqual(val, dec)

    def test_modified_value_add(self):
        s = self.cls()
        val = 'myvalue'
        enc = str(s.sign(val)) + 'F'
        print("INFO: Encoded %s -> %s" % (val, enc))
        self.assertRaises(SignatureError, s.unsign, enc)

    def test_modified_value_alter(self):
        s = self.cls()
        val = 'myvalue'
        enc_raw = str(s.sign(val))
        print("INFO: Encoded %s -> %s" % (val, enc_raw))
        enc = _alter_str(enc_raw, 3)
        print("INFO: ALTERED %s -> %s" % (enc_raw, enc))
        self.assertRaises(SignatureError, s.unsign, enc)


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

    def test_sign_unsign_str(self):
        s = self.cls()
        val = 'myvalue'
        enc = str(s.sign(val))
        print("INFO: Encoded %s -> %s" % (val, enc))
        (dec, t) = s.unsign(enc)
        print("INFO: Decoded %s -> %s" % (enc, dec))
        self.assertEqual(val, dec)

    def test_timestamp_float(self):
        s = self.cls()
        val = 'myvalue'
        enc = str(s.sign(val))
        print("INFO: Encoded %s -> %s" % (val, enc))
        (dec, t) = s.unsign(enc)
        print("INFO: Decoded %s -> %s" % (enc, dec))
        self.assertIsInstance(t, float)

    def test_encode_decode_timestamp(self):
        enc = self.cls.encode_timestamp()
        dec = self.cls.decode_timestamp(enc)
        print("INFO: Decoded %s -> %s" % (enc, dec))
