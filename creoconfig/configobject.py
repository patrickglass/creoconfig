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
from exceptions import (
    TooManyRetries,
    IllegalArgumentError
)


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
                raise IllegalArgumentError(
                    "'default' must be the same base class as 'type': "
                    "%s != %s" % (self.default, self.returntype))

        # Choices should always be stores as string type
        if choices:
            if isinstance(choices, (str, unicode)):
                raise IllegalArgumentError(
                    "'choices' must be iterable which is not a string.")
            for x in choices:
                if not isinstance(x, self.returntype):
                    raise IllegalArgumentError(
                        "'choices' must be iterable and the same class as "
                        "'type'. Item type mismatch for: "
                        "%s != %s" % (x, self.returntype))

        # map choices to string items since all comparasons are string based.
        self.choices = map(str, choices)

    def __repr__(self):
        return "%s %s: %s (%s)" % (self.name, self.returntype,
                                   self.choices, self.default)

    def prompt(self):

        self.msg = self.prefix

        if self.choices:
            self.msg += " [%s]" % ', '.join(self.choices)

        if self.default:
            self.msg += " (%s)" % str(self.default)

        self.msg += ': '

        while True:
            val = raw_input(self.msg)

            if self.retries < 0:
                    raise TooManyRetries("You can only select an option "
                                         "from the specified list! Exiting...")

            self.retries -= 1

            # At the prompt entering '?' will print the help
            # for the item if available.
            if self.help and val == '':
                print("Help for %s:\n\t%s" % (self.name, self.help))
            elif self.help and val == '?':
                print("Help for %s:\n\t%s" % (self.name, self.help))

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
                print("Could not interpret your answer '%s' as %s. Please "
                      "try again!" % (val, self.returntype))
                continue
