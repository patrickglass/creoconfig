"""
RedisStorageBackend
"""
import redis
import fakeredis
from creoconfig.storagebackend import MemStorageBackend

class RedisStorageBackend(MemStorageBackend):
    def __init__(self, host='localhost', port=6379, db=0, password=None, connection=redis.StrictRedis, *args, **kwargs):
        self.host = host
        self.port = port
        self.db = db
        self.store = connection(host=self.host,
                                port=self.port,
                                db=self.db,
                                password=password)

    def __setitem__(self, key, value):
        return self.store.set(key, value)

    def __getitem__(self, key):
        """Returns the value of the stored key
        Will raise KeyError if key is not found
        """
        val = self.store.get(key)
        if not val:
            raise KeyError("Key '%s' was not found." % key)
        return val

    def __delitem__(self, key):
        if not self.store.delete(key):
            raise KeyError("Could not find key '%s' to delete." % key)

    def __iter__(self):
        for k in self.store.keys('*'):
            yield k

    def __len__(self):
        return len(self.store.keys('*'))

    def flush(self):
        return self.store.flushdb()
