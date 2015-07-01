"""
creoconfig

Allows the central control and management of applications via
a centralized configuration management system.
"""
import re
import logging
import collections
import configobject
from exceptions import BatchModeUnableToPrompt
from storagebackend import MemStorageBackend, XmlStorageBackend


logger = logging.getLogger(__name__)


# This is a global environment settings attribute dictionary
# it is used for storing all config information once read in.
class Config(collections.MutableMapping):
    """"
    This is a global environment settings attribute dictionary
    it is used for storing all config information once read in.
    """

    def __init__(self, filename=None, defaults={}, batch=False, *args, **kwargs):
        """Defined the config variables and their validation methods

        filename - if you wish the configuration to persist specify save location
        """
        if filename is None:
            backend = MemStorageBackend()
        else:
            backend = XmlStorageBackend(filename)
        super(Config, self).__setattr__('_store', backend)
        super(Config, self).__setattr__('_isbatch', batch)
        # Store the variables which have a help menu. When one of these
        # is accessed and not found it will start a interactive prompt.
        # If batch mode is enabled then an Exception will be thrown
        super(Config, self).__setattr__('_available_keywords', [])

        # add the defaults if any were specified
        for k, v in defaults.iteritems():
            self._set(k, v)

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

    def last_modified(self, key):
        return self._store.last_modified(key)

    def __getitem__(self, key):
        logger.debug("Config.__getitem__(%s)" % key)
        return self.get(key)

    def __getattr__(self, key):
        """__get_attr__ will raise the correct exception if key is not found"""
        logger.debug("Config.__getattr__(%s)" % key)
        try:
            return self.get(key)
        except KeyError, msg:
            raise AttributeError(msg)

    def _set(self, key, value):
        logger.debug("Config.set(%s, %s)" % (key, value))
        return self._store.set(key, str(value))

    def __setitem__(self, key, value):
        logger.debug("Config.__setitem__(%s, %s)" % (key, value))
        return self._set(key, value)

    def __setattr__(self, key, value):
        logger.debug("Config.__setattr__(%s, %s)" % (key, value))
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
                    raise BatchModeUnableToPrompt(
                        "%s not found. Please exit batchmode to start wizard "
                        "or set this variable manually." % k.name)
                val = k.prompt()
                self._set(k.name, val)
        return True
