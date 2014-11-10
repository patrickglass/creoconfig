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
        self.__setattr__('_meta', attrdict.AttrDict(), force=True)
        # Update storagebackends as soon as a value changes
        self._meta.backends = kwargs.pop('backends', None)
        self._meta.autosync = kwargs.pop('autosync', True)
        self._meta.batchmode = kwargs.pop('batch', False)
        # Store the variables which have a help menu. When one of these
        # is accessed and not found it will start a interactive prompt.
        # If batch mode is enabled then an Exception will be thrown
        self._meta.available_keywords = []
        return super(Config, self).__init__(*args, **kwargs)

    def sync(self):
        return True

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

    def load(self):
        pass


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
                    print("Answers must be not be empty. Please try again!")
                    continue

            # Validate self.choices
            if self.choices and val not in self.choices:
                if self.retries < 0:
                    raise TooManyRetries("You can only select an option from the specified list! Exiting...")
                else:
                    print("You have selected an invalid answer! Please try again.")
                    continue

            try:
                return self.returntype(val)
            except ValueError:
                print("Invalid answer. Could not interpret your response '%s' as %s. Please try again!" % (val, self.returntype))
                continue

