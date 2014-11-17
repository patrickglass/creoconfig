#!/usr/bin/env python
"""
Module test_creoconfig

UnitTest framework for validating CreoConfig
"""
import os
import sys
import uuid
sys.path.append(os.path.realpath('.'))

from creoconfig import Config
from creoconfig.exceptions import *
from creoconfig import FileStorageBackend



def gen_new_filename(base='tmp_interactive_save_%s.db'):
    f = base % uuid.uuid1()
    print("INFO: Generated new file: %s" % f)
    return f

filename = gen_new_filename()

def interactive_prompt():
    s = FileStorageBackend(filename)
    c = Config(backend=s)

    print("Configuration Start:")
    for k,v in c.iteritems():
        print("\t%s: %s" % (k, v))

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
        choices=['a', 'b', 'c', '10'],
        default='c')

    c.prompt()

    print("Configuration End:")
    for k,v in c.iteritems():
        print("\t%s: %s" % (k, v))

    c.close()

if __name__ == '__main__':
    print "INFO: Running interactive tests!"
    interactive_prompt()
