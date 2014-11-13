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
import attrdict
from exceptions import BatchModeUnableToPromt, TooManyRetries, IllegalArgumentError


# This is a global environment settings attribute dictionary
# it is used for storing all config information once read in.
class Config(attrdict.AttrDict):
    """Defined the config variables and their validation methods"""
    def __init__(self, *args, **kwargs):
        # Define an internal structure to hold Config internal settings
        super(Config, self).__setattr__('_meta', attrdict.AttrDict(), force=True)
        # Update storagebackends as soon as a value changes
        self._meta.backend = kwargs.pop('backend', None)
        self._meta.autosync = kwargs.pop('autosync', True)
        self._meta.batchmode = kwargs.pop('batch', False)
        # Store the variables which have a help menu. When one of these
        # is accessed and not found it will start a interactive prompt.
        # If batch mode is enabled then an Exception will be thrown
        self._meta.available_keywords = []
        return super(Config, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        """
        get will lookup the key in the current dictionary and return the
        value. If the key is missing it will check if an 'add_option' has been
        called with this name. This will allow the add_option to prompt the
        user or to use the default option if supplied.
        """
        try:
            return super(Config, self).__getitem__(key)
        except KeyError:
            # Key was not found in local dictionary
            # Check the backend if it is storing the value
            val = None
            if self._meta.backend:
                val = self._meta.backend.get(key)
            if val:
                self['key'] = val
            else:
                # Key was not found so we will check the available options
                # in batch mode we will just consider options with a default
                # option
                val = self._auto_prompt(key)
            return val

    def __getattr__(self, key):
        """
        get will lookup the key in the current dictionary and return the
        value. If the key is missing it will check if an 'add_option' has been
        called with this name. This will allow the add_option to prompt the
        user or to use the default option if supplied.
        """
        try:
            return super(Config, self).__getattr__(key)
        except AttributeError:
            # Key was not found in local dictionary
            # Check the backend if it is storing the value
            val = None
            if self._meta.backend:
                val = self._meta.backend.get(key)
            if val:
                self['key'] = val
            else:
                # Key was not found so we will check the available options
                # in batch mode we will just consider options with a default
                # option
                val = self._auto_prompt(key)
            return val

    def __setitem__(self, key, value):
        """
        Responsible for actually adding/changing a key-value pair. This
        needs to be separated out so that setattr and setitem don't
        clash.
        """
        # Save the result to the backend if enabled
        if self._meta.backend:
            self._meta.backend.set(key, value)
        return super(Config, self).__setitem__(key, value)


    def __setattr__(self, key, value, force=False):
        """
        Responsible for actually adding/changing a key-value pair. This
        needs to be separated out so that setattr and setitem don't
        clash.
        """
        # Save the result to the backend if enabled
        # if force is enabled we dont want to save to backend
        # as this is only used to create internal variables
        if self._meta.backend and not force:
            self._meta.backend.set(key, value)
        return super(Config, self).__setattr__(key, value, force)


    def __delitem__(self, key):
        """
        Responsible for actually deleting a key-value pair. This needs
        to be separated out so that delattr and delitem don't clash.
        """
        # Save the result to the backend if enabled
        if self._meta.backend:
            self._meta.backend.delete(key)
        return super(Config, self).__delitem__(key)


    def __delattr__(self, key):
        """
        Responsible for actually deleting a key-value pair. This needs
        to be separated out so that delattr and delitem don't clash.
        """
        # Save the result to the backend if enabled
        if self._meta.backend:
            self._meta.backend.delete(key)
        return super(Config, self).__delattr__(key)

    def _auto_prompt(self, key):
        """
        Key was not found so we will check the available options
        in batch mode we will just consider options with a default option
        """
        print "INFO: AttributeError Exception handler"
        for k in self._meta.available_keywords:
            if k.name == key:
                if self._meta.batchmode:
                    if k.default:
                        print "INFO: default was set"
                        val = k.default
                    else:
                        # We can't handle anything in batchmode
                        raise
                else:
                    val = k.prompt()
                self['key'] = val
                return val
        # Unable to handle AttributeError, reraise it.
        raise

    def sync(self):
        """
        Ensures the local dictionary is synced up with the backend
        returns False on error with sync
        """
        try:
            if self._meta.backend:
                return self._meta.backend.sync()
        except AttributeError:
            pass
        return False

    def close(self):
        """
        Closes the backend if it supports it
        """
        try:
            if self._meta.backend:
                return self._meta.backend.close()
        except AttributeError:
            pass
        return False

    def add_option(self, *args, **kwargs):
        self._meta.available_keywords.append(ConfigObject(*args, **kwargs))
        return True

    def prompt(self):
        for k in self._meta.available_keywords:
            if k.name not in self:
                if self._meta.batchmode:
                    raise BatchModeUnableToPromt("%s not found. Please exit batchmode to start wizard or set this variable manually." % k.name)
                val = k.prompt()
                self[k.name] = val
        return True

    # def load(self):
    #     pass


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

