"""
creoconfig exceptions
"""


class ConfigException(Exception):
    """Base class for all application generated exceptions"""
    pass

class InvalidFieldName(ConfigException):
    """Base class for all application generated exceptions"""
    pass

class BatchModeUnableToPromt(ConfigException):
    """
    Thrown when Config is in batch mode and a key was not found
    Normally this would invoke the wizard to prompt the user to fill in
    a value
    """
    pass

class TooManyRetries(ConfigException):
    """User failed to enter valid options to many times"""
    pass
