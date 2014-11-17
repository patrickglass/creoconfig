"""
StorageBackend
"""
import shelve
import redis
import collections
import ConfigParser


class MemStorageBackend(collections.MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = {}

    def __setitem__(self, key, value):
        self.store[key] = value
        return True

    def set(self, key, value):
        return self.__setitem__(key, value)

    def __getitem__(self, key):
        return self.store[key]

    def get(self, key):
        return self.__getitem__(key)

    def __delitem__(self, key):
        del self.store[key]

    def delete(self, key):
        return self.__delitem__(key)

    def __iter__(self):
        return self.store.__iter__()

    def __len__(self):
        return len(self.store)

    def __contains__(self, item):
        return (item in self.store)


class FileStorageBackend(MemStorageBackend):
    def __init__(self, filename, flag='c', *args, **kwargs):
        """
        Params:
            flag: same interpretation as anydbm.open
                r Open existing database for reading only
                w Open existing database for reading and writing
                c Open database for reading and writing, creating it if it doesn't exist (default)
                n Always create a new, empty database, open for reading and writing
        """
        self.store = shelve.open(filename, flag, writeback=True)
        # self.store
        # self.sync()
        # print("INFO: Opening %s" % filename)
        # print("INFO: Data: %s" % str(self.store))

    def __del__(self):
        self.close()

    def close(self):
        return self.store.close()

    def sync(self):
        return self.store.sync()


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


class ConfigParserStorageBackend(FileStorageBackend):
    def __init__(self, filename, section='DEFAULT', *args, **kwargs):
        self.filename = filename
        self.section = section
        self.store = ConfigParser.RawConfigParser()
        # self.store.add_section(self.section)
        self.store.read(self.filename)

    def __setitem__(self, key, value):
        self.store.set(self.section, key, value)
        return True

    def __getitem__(self, key):
        """Returns the value of the stored key
        Will raise KeyError if key is not found
        """
        try:
            return self.store.get(self.section, key)
        except ConfigParser.NoOptionError, msg:
            raise KeyError(msg)

    def __delitem__(self, key):
        if not self.store.remove_option(self.section, key):
            raise KeyError("Could not find key '%s' to delete." % key)

    def __contains__(self, item):
        try:
            return bool(self.__getitem__(item))
        except KeyError:
            return False

    def sync(self):
        with open(self.filename, 'wb') as configfile:
            self.store.write(configfile)

    def close(self):
        self.sync()

    def __del__(self):
        self.close()

    def __iter__(self):
        for k,v in self.store.items(self.section):
            yield k

    def __len__(self):
        return len(self.store.items(self.section))
