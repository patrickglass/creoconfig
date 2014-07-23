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
        pass

