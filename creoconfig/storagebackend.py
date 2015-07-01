"""
StorageBackend
"""
import os
import time
import hmac
import hashlib
import logging
import collections
import ConfigParser
try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree
from xml.dom import minidom


logger = logging.getLogger(__name__)


class MemStorageBackend(collections.MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = {}

    def __setitem__(self, key, value):
        self.store[key] = value
        return True

    def __getitem__(self, key):
        return self.store[key]

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return self.store.__iter__()

    def __len__(self):
        return len(self.store)

    def set(self, key, value):
        return self.__setitem__(key, value)

    def get(self, key):
        """Override the default get since we want to throw an exception
        if a key is not found
        """
        return self.__getitem__(key)

    def delete(self, key):
        return self.__delitem__(key)

    def last_modified(self, key):
        """Not supported yet for this backend"""
        return None


class FileStorageBackend(MemStorageBackend):
    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        super(FileStorageBackend, self).__init__(*args, **kwargs)

    def sync(self):
        raise RuntimeError("Must be implemented in child class.")


class ConfigParserStorageBackend(FileStorageBackend):
    def __init__(self, filename, section='DEFAULT', *args, **kwargs):
        self.filename = filename
        self.section = section
        self.store = ConfigParser.RawConfigParser()
        # self.store.add_section(self.section)
        self.store.read(self.filename)
        # with open(self.filename) as f:
        #     self.store.readfp(f)

    def __setitem__(self, key, value):
        self.store.set(self.section, key, value)
        self.sync()
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
        self.sync()

    def __iter__(self):
        for k, v in self.store.items(self.section):
            yield k

    def __len__(self):
        return len(self.store.items(self.section))

    def sync(self):
        with open(self.filename, 'wb') as f:
            self.store.write(f)


class XmlStorageBackend(ConfigParserStorageBackend):
    def __init__(self, filename, hashentries=True, *args, **kwargs):
        # Specify the name of the xml element for variables
        self.version = '1.0.0'
        self.filename = filename
        self.hashentries = hashentries
        if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
            with open(self.filename) as f:
                try:
                    self.store = ElementTree.parse(f)
                except ElementTree.ParseError:
                    raise RuntimeError("""FATAL: XML settings file is invalid!
                        Please check the file '%s' with an xml linter to ensure
                        the syntax is correct and that is also conforms to the
                        formatting for a valid config file. If in doubt rename
                        this file and run this command again to generate a
                        clean template.""" % self.filename)
                self.version = self.store.getroot().get('version')
        else:
            # Create a basic config file with no variables
            config = ElementTree.Element('config')
            config.set('version', self.version)
            self.store = ElementTree.ElementTree(config)

        if self.version != '1.0.0':
            print "XML file is not a valid configuration version."

    @staticmethod
    def sign(*args):
        """
        generates a hash signature from the input arguments which
        can be used to check for future tampering.
        """
        sig = hmac.new(b'creoconfig.storagebackend', digestmod=hashlib.sha1)
        for arg in args:
            sig.update(bytes(arg))
        return sig.digest().encode("base64").rstrip('\n')

    @staticmethod
    def _compare_digest(x, y):
        return x == y
        if not (isinstance(x, bytes) and isinstance(y, bytes)):
            raise TypeError("both inputs should be instances of bytes")
        if len(x) != len(y):
            return False
        result = 0
        for a, b in zip(x, y):
            result |= a ^ b
        return (result == 0)

    @staticmethod
    def validate(signature, *args):
        gensig = XmlStorageBackend.sign(*args)
        return XmlStorageBackend._compare_digest(
            bytes(gensig), bytes(signature))

    def __setitem__(self, key, value):
        # If the value exists just replace it otherwise create new
        if not isinstance(key, basestring):
            raise TypeError("Key must be of string type")
        node = None
        for var in self.store.iter('var'):
            if var.find('name').text.strip() == key:
                node = var
        if node is None:
            node = ElementTree.SubElement(self.store.getroot(), 'var')
        node_name = ElementTree.SubElement(node, 'name')
        node_value = ElementTree.SubElement(node, 'value')
        node_name.text = key
        node_value.text = str(value)
        # We also will store the original type of the value
        node_value.set('type', type(value).__name__)

        # Check if we should add the hash signature
        if self.hashentries:
            node.set('timestamp', str(time.time()))
            sig = self.sign(key, str(value), type(value).__name__)
            node.set('signature', sig)
        # Save this new information to disk
        self.sync()
        return True

    def __getitem__(self, key):
        """TODO: Still need to use 'type' attr to cast value"""
        for var in self.store.iter('var'):
            if var.find('name').text.strip() == key:
                return var.find('value').text.strip() or var.find('default').text.strip()
        raise KeyError("name %s was not found in xml file!" % key)

    def last_modified(self, key):
        """
        Returns the last modified time epoch float if the key exists

        raises a keyerror if key does not exist.
        """
        for var in self.store.iter('var'):
            if var.find('name').text.strip() == key:
                if self.hashentries:
                    ts = var.get('timestamp')
                    # Need to detect of config was modified outside of this
                    # program. Check the signature hash to ensure it is the
                    # same
                    val = var.get('value')
                    typ = var.get('type')
                    sig = var.get('signature')
                    valid = self.validate(sig, key, val, typ)
                    if valid:
                        logger.debug("Signature for key '%s' is valid!" % key)
                        return float(ts)
                    else:
                        logger.warn("Key '%s' signature mismatch. Setting last modified time to NOW()" % key)
                        return time.time()
                else:
                    return None
        raise KeyError("name %s was not found in xml file!" % key)

    def __delitem__(self, key):
        for var in self.store.findall('var'):
            if var.find('name').text.strip() == key:
                self.store.getroot().remove(var)
                # Save this update disk
                self.sync()
                return True
        raise KeyError("key %s was not found in config file" % key)

    def __iter__(self):
        data = {}
        for var in self.store.findall('var'):
            data[var.find('name').text.strip()] = var.find('value').text.strip()
        return iter(data)

    def __len__(self):
        return len(self.store.findall('var'))

    def sync(self):
        """Write the xml data to the file with expanded subelements"""
        with open(self.filename, 'w+') as f:
            f.write(self.prettify(self.store.getroot()))
            # self.store.write(f, method='html')

    @staticmethod
    def prettify(elem):
        """Return a pretty-printed XML string for the Element."""
        rough_string = ElementTree.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")
