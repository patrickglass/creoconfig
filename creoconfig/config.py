"""
creoconfig

Allows the central control and management of applications via
a centralized configuration management system.
"""
try:
    """ReadLine will enhance the raw_input and allow history"""
    import readline
except ImportError:
    pass
import re
import collections
from exceptions import (
    BatchModeUnableToPromt,
    TooManyRetries,
    IllegalArgumentError
)
from storagebackend import MemStorageBackend

# This is a global environment settings attribute dictionary
# it is used for storing all config information once read in.
class Config(collections.MutableMapping):
    """"
    This is a global environment settings attribute dictionary
    it is used for storing all config information once read in.
    """

    def __init__(self, backend=MemStorageBackend(), batch=False, *args, **kwargs):
        """Defined the config variables and their validation methods"""
        # self._store = backend
        super(Config, self).__setattr__('_store', backend)
        # self._isbatch = batch
        super(Config, self).__setattr__('_isbatch', batch)
        # Store the variables which have a help menu. When one of these
        # is accessed and not found it will start a interactive prompt.
        # If batch mode is enabled then an Exception will be thrown
        # self._available_keywords = []
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
            BatchModeUnableToPromt: if prompting is possible but
                `batch` is enabled.
            TooManyRetries: When prompted user is unable to enter in
                a valid value based on `add_option` specifications.
        """
        # Backends get will return None if key is not found
        val = self._store.get(key, default)
        if val is None and not default:
            return self._auto_prompt(key)
        return val

    def __getitem__(self, key):
        return self.get(key)

    def __getattr__(self, key):
        """__get_attr__ will raise the correct exception if key is not found"""
        try:
            return self.get(key)
        except KeyError, msg:
            raise AttributeError(msg)

    def _set(self, key, value):
        """
        Responsible for actually adding/changing a key-value pair. This
        needs to be separated out so that setattr and setitem don't
        clash.
        """
        return self._store.set(key, value)

    def __setitem__(self, key, value):
        return self._set(key, value)

    def __setattr__(self, key, value):
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
                self['key'] = val
                return val
        # Unable to prompt user for value
        raise KeyError("key '%s' was not found.")

    def sync(self):
        """
        Ensures the local dictionary is synced up with the backend
        returns False on error with sync
        """
        try:
            if self._store:
                return self._store.sync()
        except AttributeError:
            pass
        return False

    def close(self):
        """
        Closes the backend if it supports it
        """
        try:
            if self._store:
                return self._store.close()
        except AttributeError:
            pass
        return False

    def add_option(self, *args, **kwargs):
        self._available_keywords.append(ConfigObject(*args, **kwargs))
        return True

    def prompt(self):
        for k in self._available_keywords:
            if k.name not in self._store:
                if self._isbatch:
                    raise BatchModeUnableToPromt("%s not found. Please exit batchmode to start wizard or set this variable manually." % k.name)
                val = k.prompt()
                self[k.name] = val
        return True


def prompt_user(*args, **kwargs):
    """
    Read a string from standard input.  The trailing newline is stripped.
    If the user hits EOF (Unix: Ctl-D, Windows: Ctl-Z+Return), raise EOFError.
    On Unix, GNU readline is used if enabled.  The prompt string, if given,
    is printed without a trailing newline before reading.
    """
    return raw_input(*args, **kwargs)


class ConfigObject(object):
    """
    Stores all the information about a variable. This is used to
    create a useful interactive prompt for the user to enter in the value.
    """
    def __init__(self, name, prefix='', help=None, type=None,
                 choices={}, default=None, retries=3):
        self.name = str(name)
        self.prefix = prefix
        self.help = help
        self.returntype = type or str

        self.default = default
        self.retries = int(retries)

        if self.returntype not in [int, float, long, complex, str, unicode, list, tuple, bytearray, buffer, xrange]:
            raise IllegalArgumentError("%s is not a python base type." % self.returntype)

        # Ensure that default value is of the correct type
        if self.default:
            if not isinstance(self.default, self.returntype):
                raise IllegalArgumentError("'default' must be the same base class as 'type': %s != %s" % (self.default, self.returntype))

        # Choices should always be stores as string type
        if choices:
            if isinstance(choices, (str, unicode)):
                raise IllegalArgumentError("'choices' must be iterable which is not a string.")
            for x in choices:
                if not isinstance(x, self.returntype):
                    raise IllegalArgumentError("'choices' must be iterable and the same class as 'type'. Item type mismatch for: %s != %s" % (x, self.returntype))

        # map choices to string items since all comparasons are string based.
        self.choices = map(str, choices)

    def __repr__(self):
        return "%s %s: %s (%s)" % (self.name, self.returntype, self.choices, self.default)

    def prompt(self):

        self.msg = self.prefix

        if self.choices:
            self.msg += " [%s]" % ', '.join(self.choices)

        if self.default:
            self.msg += " (%s)" % str(self.default)

        self.msg += ': '

        while True:
            val = prompt_user(self.msg)

            if self.retries < 0:
                    raise TooManyRetries("You can only select an option from the specified list! Exiting...")

            # At the prompt entering '?' will print the help
            # for the item if available.
            if self.help and val == '':
                print("Help for %s:\n\t%s" % (self.name, self.help))
            elif self.help and val == '?':
                print("Help for %s:\n\t%s" % (self.name, self.help))
            else:
                self.retries -= 1

            # Responses must not be empty if a default is not set
            if val == '':
                if self.default:
                    val = self.default
                else:
                    print("Answer must be not be empty. Please try again!")
                    continue

            # Validate self.choices
            if self.choices and val not in self.choices:
                print("You have selected an invalid answer! Please try again.")
                continue

            try:
                return self.returntype(val)
            except ValueError:
                print("Could not interpret your answer '%s' as %s. Please try again!" % (val, self.returntype))
                continue
            return val

