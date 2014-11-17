"""
creoconfig

Allows the central control and management of applications via
a centralized configuration management system.
"""
import re
import collections
import configobject
from exceptions import BatchModeUnableToPrompt
from storagebackend import MemStorageBackend


# This is a global environment settings attribute dictionary
# it is used for storing all config information once read in.
class Config(collections.MutableMapping):
    """"
    This is a global environment settings attribute dictionary
    it is used for storing all config information once read in.
    """

    def __init__(self, backend=None, batch=False, *args, **kwargs):
        """Defined the config variables and their validation methods"""
        if backend is None:
            backend = MemStorageBackend()
        super(Config, self).__setattr__('_store', backend)
        super(Config, self).__setattr__('_isbatch', batch)
        # Store the variables which have a help menu. When one of these
        # is accessed and not found it will start a interactive prompt.
        # If batch mode is enabled then an Exception will be thrown
        super(Config, self).__setattr__('_available_keywords', [])

    @classmethod
    def _check_key_name(cls, name):
        """Checks the name is valid for creating a new attribute

        Using attribute assignments we only want to allow simple string
        name for keys. We also check the current class for a name collision
        """
        return (isinstance(name, basestring) and
                re.match('^[A-Za-z][A-Za-z0-9_]*$', name) and
                not hasattr(cls, name))

    def _delete(self, key):
        """Deletes a value given the `key`

        Responsible for actually deleting a key-value pair. This needs
        to be separated out so that delattr and delitem don't clash.
        """
        return self._store.delete(key)

    def __delitem__(self, key):
        return self._delete(key)

    def __delattr__(self, key):
        try:
            return self._delete(key)
        except KeyError, msg:
            raise AttributeError(msg)

    def get(self, key, default=None):
        """Gets the value associated with the key

        First tests the backend to see if the key is stored. If the key does
        not exists and a `default` value was passed in then this will be
        returned. If no value is stored and default is not set then it will
        try to see if someone has defined the key via the `add_option` method.
        As long as we are not in batchmode the class will prompt the user to
        suppply the value as per the configuration. This value will then be
        stored in the backend for later use.

        Params:
            key: string identifier for the value
            default: if key is not found the default is returned.

        Returns:
            Value stored via the `key` or and Exception

        Raises:
            KeyError: If the key is not found and default is not set
                KeyError will be raised.
            BatchModeUnableToPrompt: if prompting is possible but
                `batch` is enabled.
            TooManyRetries: When prompted user is unable to enter in
                a valid value based on `add_option` specifications.
        """
        try:
            val = self._store.get(key)
        except KeyError:
            val = default
            if val is None and not default:
                return self._auto_prompt(key)
        return val

    def __getitem__(self, key):
        # print("INFO: Config.__getitem__(%s)" % key)
        return self.get(key)

    def __getattr__(self, key):
        """__get_attr__ will raise the correct exception if key is not found"""
        # print("INFO: Config.__getattr__(%s)" % key)
        try:
            return self.get(key)
        except KeyError, msg:
            raise AttributeError(msg)

    def _set(self, key, value):
        # print("INFO: Config.set(%s, %s)" % (key, value))
        return self._store.set(key, str(value))

    def __setitem__(self, key, value):
        # print("INFO: Config.__setitem__(%s, %s)" % (key, value))
        return self._set(key, value)

    def __setattr__(self, key, value):
        # print("INFO: Config.__setattr__(%s, %s)" % (key, value))
        return self._set(key, value)

    def __iter__(self):
        return self._store.__iter__()

    def __len__(self):
        return len(self._store)

    def _auto_prompt(self, key):
        """
        Key was not found so we will check the available options
        in batch mode we will just consider options with a default option
        """
        for k in self._available_keywords:
            if k.name == key:
                if self._isbatch:
                    if k.default:
                        val = k.default
                    else:
                        break
                else:
                    val = k.prompt()
                self._set(key, val)
                return val
        # Unable to prompt user for value
        raise KeyError("key '%s' was not found.")

    def sync(self):
        """
        Ensures the local dictionary is synced up with the backend
        """
        return self._store.sync()

    def close(self):
        return self._store.close()

    def enable_batch(self):
        super(Config, self).__setattr__('_isbatch', True)

    def disable_batch(self):
        super(Config, self).__setattr__('_isbatch', False)

    def add_option(self, *args, **kwargs):
        self._available_keywords.append(
            configobject.ConfigObject(*args, **kwargs)
        )
        return True

    def prompt(self):
        for k in self._available_keywords:
            if k.name not in self._store:
                if self._isbatch:
                    raise BatchModeUnableToPrompt("%s not found. Please exit batchmode to start wizard or set this variable manually." % k.name)
                val = k.prompt()
                self._set(k.name, val)
        return True

import time
import calendar
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
        return (data[0], int(data[1]))

    def get(self, key, default=None):
        value = super(TimestampedConfig, self).get(key, default=None)
        return self._extract_value(str(value))[0]

    def _set(self, key, value, timestamp=None):
        value = self._gen_value(value, timestamp)
        return super(TimestampedConfig, self)._set(key, value)

    def last_modified(self, key):
        """Returns the last time the key was modified"""
        value = super(TimestampedConfig, self).get(key, default=None)
        return self._extract_value(value)[1]
