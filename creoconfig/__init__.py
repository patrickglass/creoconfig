"""
creoconfig
"""
import exceptions
from config import Config
from storagebackend import (
    MemStorageBackend,
    FileStorageBackend,
    RedisStorageBackend,
    ConfigParserStorageBackend
)



__all__ = ['creoconfig', 'exceptions', 'storagebackend']

__title__ = 'creoconfig'
__version__ = '0.1.0'
__author__ = 'Patrick Glass'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014 Patrick Glass'
