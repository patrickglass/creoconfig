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
                k.prompt()


class ConfigObject(object):
    """
    Stores all the information about a variable. This is used to
    create a useful interactive prompt for the user to enter in the value.
    """
    def __init__(self, name, prefix=None, help=None, dest=None,
                   type=None, choices=None, default=None, retries=3):
        self.name = name
        self.prefix = prefix
        self.help = help
        self.dest = dest
        self.type = type
        self.choices = choices
        self.default = default
        self.retries = retries

    def prompt(self):

        self._pfx = self.prefix

        if self.choices:
            self._pfx += " [%s]" % ', '.join(self.choices)

        if self.default:
            self._pfx += " (%s): " % self.default

        while True:
            val = raw_input(self._pfx)
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
            return val

