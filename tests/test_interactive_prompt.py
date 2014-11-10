#!/usr/bin/env python
"""
Module test_interactive_prompt

UnitTest framework for validating CreoConfig
"""
import unittest

import os
import sys
sys.path.append(os.path.realpath('.'))

from creoconfig import Config
from creoconfig.exceptions import *
from creoconfig.fields import *


class TestInteractivePrompt(unittest.TestCase):

	@unittest.skip("This should only be run interactively. Skip during batch testing.")
	def test_prompt(self):
		c = Config()
		c.add_option('strkey',
			prefix='Please enter string',
			help='This is a string key')
		c.add_option('intkey',
			prefix='Please enter integer value',
			help='This is a int key',
			type=int)
		c.add_option('choice_key',
			prefix='Please enter one of the integer choices',
			help='This is a int key which only allows certail values',
			type=int,
			choices=[1, 2, 3, 10])
		c.add_option('choice_key_str',
			prefix='Please choose one of the string values',
			help='This is a string key which only allows certail values',
			type=str,
			choices=['a', 'b', 'c', '10'])

		c.prompt()

		print("Configuration:")
		for k,v in c.iteritems():
			print("\t%s: %s" % (k, v))
