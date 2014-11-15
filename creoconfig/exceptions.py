"""
creoconfig exceptions
"""


class ConfigException(Exception):
    """Base class for all application generated exceptions"""
    pass

class IllegalArgumentError(ConfigException):
    """Thrown when the arguments passed in need to be fixed."""
    pass

class BatchModeUnableToPrompt(ConfigException):
    """
    Thrown when Config is in batch mode and a key was not found
    Normally this would invoke the wizard to prompt the user to fill in
    a value
    """
    pass

class TooManyRetries(ConfigException):
    """User failed to enter valid options to many times"""
    pass

# class KeyNotFound(ConfigException)
#     """Key supplied was not found"""
#     pass
