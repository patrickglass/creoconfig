"""
creoconfig

Allows the central control and management of applications via
a centralized configuration management system.
"""


class Config(object):
    """Defined the config variables and their validation methods"""
    def __init__(self, server=None, cache_file=None):
        self.server = server
        self.cache_file = cache_file

    def sync(self):
        return True

    def add_option(self, name, help=None, dest=None,
                   type=None, choices=None, default=None):
        pass
