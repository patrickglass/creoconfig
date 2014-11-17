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

class TimestampedConfig(test_creoconfig.TestCaseConfig):
    pass
