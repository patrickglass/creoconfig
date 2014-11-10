"""
creoconfig

Allows the central control and management of applications via
a centralized configuration management system.
"""
import attrdict
from exceptions import BatchModeUnableToPromt, TooManyRetries


# This is a global environment settings attribute dictionary
# it is used for storing all config information once read in.
class Config(attrdict.AttrDict):
    """Defined the config variables and their validation methods"""
    def __init__(self, *args, **kwargs):
        # Update storagebackends as soon as a value changes
        self.__setattr__('_backends', kwargs.pop('backends', None), force=True)
        self.__setattr__('_autosync', kwargs.pop('autosync', True), force=True)
        self.__setattr__('_batchmode', kwargs.pop('batch', False), force=True)
        # Store the variables which have a help menu. When one of these
        # is accessed and not found it will start a interactive prompt.
        # If batch mode is enabled then an Exception will be thrown
        self.__setattr__('_available_keywords', [], force=True)
        return super(Config, self).__init__(*args, **kwargs)

    def sync(self):
        return True

    def add_option(self, *args, **kwargs):
        self._available_keywords.append(ConfigObject(*args, **kwargs))

    def prompt(self):
        for k in self._available_keywords:
            if k.name not in self:
                if self._batchmode:
                    raise BatchModeUnableToPromt("%s not found. Please exit batchmode to start wizard or set this variable manually." % k.name)
                val = k.prompt()
                print("INFO: Prompt returned: %s" % str(val))
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
    def __init__(self, name, prefix='', help=None, dest=None,
                   type=None, choices={}, default=None, retries=3):
        self.name = str(name)
        self.prefix = prefix
        self.help = help
        self.dest = dest
        # Not used yet
        self.type = type or str
        self.choices = map(str, choices)
        self.default = default
        self.retries = int(retries)

    def prompt(self):
        self._pfx = self.prefix

        if self.choices:
            self._pfx += " [%s]" % ', '.join(self.choices)

        if self.default:
            self._pfx += " (%s): " % str(self.default)

        while True:
            val = prompt_user(self._pfx)
            self.retries -= 1

            # If the users did not enter a value in use the default
            if self.default and val == '':
                val = self.default

            # Validate self.choices
            if self.choices and val not in self.choices:
                if self.retries < 0:
                    raise TooManyRetries("You can only select an option from the specified list! Exiting...")
                    return None
                else:
                    print("You have selected an invalid answer! Please try again.")
                    continue

            try:
                return self.type(val)
            except ValueError:
                return val

