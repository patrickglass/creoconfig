"""
creoconfig

Allows the central control and management of applications via
a centralized configuration management system.
"""
import time
import calendar
from config import Config

class TimestampedConfig(Config):

    def __init__(self, *args, **kwargs):
        sep = kwargs.pop('separator', '::')
        super(Config, self).__setattr__('_separator', sep)
        super(TimestampedConfig, self).__init__(*args, **kwargs)

    def _gen_value(self, value, timestamp=None):
        t = calendar.timegm(time.gmtime(timestamp))
        return str(value) + '::' + str(t)

    def _extract_value(self, value):
        """returns a tuple of (value, timestamp)"""
        data = value.rsplit('::')
        print data
        try:
            return (data[0], int(data[1]))
        except IndexError:
            return (data[0], None)

    def get(self, key, default=None):
        value = super(TimestampedConfig, self).get(key, default)
        return self._extract_value(str(value))[0]

    def _set(self, key, value, timestamp=None):
        value = self._gen_value(value, timestamp)
        return super(TimestampedConfig, self)._set(key, value)

    def last_modified(self, key):
        """Returns the last time the key was modified"""
        value = super(TimestampedConfig, self).get(key)
        return self._extract_value(value)[1]
