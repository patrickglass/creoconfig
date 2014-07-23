"""
creoconfig exceptions
"""


class ConfigException(Exception):
    """Base class for all application generated exceptions"""
    pass

class InvalidFieldName(ConfigException):
    """Base class for all application generated exceptions"""
    pass
