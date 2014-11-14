"""
StorageBackend
"""
import shelve
import redis
import collections


class StorageBackend(object):
    def set(self, key, value, *args, **kwargs):
        raise NotImplementedError("This method must be redefined in the subclass")

    def get(self, key, default=None, *args, **kwargs):
        raise NotImplementedError("This method must be redefined in the subclass")

    def delete(self, key, *args, **kwargs):
        raise NotImplementedError("This method must be redefined in the subclass")

    def __iter__(self):
        raise NotImplementedError("This method must be redefined in the subclass")


class MemStorageBackend(StorageBackend):
    def __init__(self, *args, **kwargs):
        self.dict = {}

    def set(self, key, value, *args, **kwargs):
        self.dict[key] = value
        return True

    def get(self, key, default=None, *args, **kwargs):
        return self.dict.get(key, default)

    def delete(self, key, *args, **kwargs):
        del self.dict[key]

    def __iter__(self):
        return self.dict.__iter__()

    # def __iter__(self):
    # for item in self.dict.items():
    #     yield item


class FileStorageBackend(MemStorageBackend):
    def __init__(self, filename, *args, **kwargs):
        self.dict = shelve.open(filename, writeback=True)

    def set(self, key, value, *args, **kwargs):
        self.dict[key] = value
        return True

    def get(self, key, default=None, *args, **kwargs):
        return self.dict.get(key, default)

    def delete(self, key, *args, **kwargs):
        del self.dict[key]

    def close(self):
        return self.dict.close()

    def sync(self):
        return self.dict.sync()

    def __del__(self):
        self.close()

    def __iter__(self):
        return self.dict.__iter__()


class RedisStorageBackend(StorageBackend):
    def __init__(self, host='localhost', port=6379, db=0, password=None, connection=redis.StrictRedis, *args, **kwargs):
        self.host = host
        self.port = port
        self.db = db
        self.r = connection(host=self.host,
                            port=self.port,
                            db=self.db,
                            password=password)

    def set(self, key, value, *args, **kwargs):
        return self.r.set(key, value)

    def get(self, key, default=None, *args, **kwargs):
        return self.r.get(key) or default

    def delete(self, key, *args, **kwargs):
        if not self.r.delete(key):
            raise KeyError("Could not find key '%s' to delete." % key)

    def __iter__(self):
        return self.r.hscan_iter()
