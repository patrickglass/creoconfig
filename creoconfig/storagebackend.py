"""
StorageBackend
"""
import shelve
import redis

class StorageBackend(object):
    def set(self, key, value, *args, **kwargs):
        raise NotImplementedError("This method must be redefined in the subclass")

    def get(self, key, default=None, *args, **kwargs):
        raise NotImplementedError("This method must be redefined in the subclass")

    def delete(self, key, *args, **kwargs):
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
        try:
            del self.dict[key]
        except KeyError:
            return False
        return True


class FileStorageBackend(MemStorageBackend):
    def __init__(self, filename, *args, **kwargs):

        self.dict = shelve.open(filename)

    def set(self, key, value, *args, **kwargs):
        self.dict[key] = value
        return True

    def get(self, key, default=None, *args, **kwargs):
        return self.dict.get(key, default)

    def delete(self, key, *args, **kwargs):
        try:
            del self.dict[key]
        except KeyError:
            return False
        return True

    def close(self):
        return self.dict.close()

    def __del__(self):
        self.close()


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
        return self.r.delete(key)
