"""
StorageBackend
"""
import os
import shelve
import collections
import ConfigParser
try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree
from xml.dom import minidom

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


class FileStorageBackend(MemStorageBackend):
    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        super(FileStorageBackend, self).__init__(*args, **kwargs)

    def sync(self):
        raise RuntimeError("Must be implemented in child class.")

    def close(self):
        raise RuntimeError("Must be implemented in child class.")

    def __del__(self):
        self.close()


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

    def __iter__(self):
        for k,v in self.store.items(self.section):
            yield k

    def __len__(self):
        return len(self.store.items(self.section))

    def sync(self):
        with open(self.filename, 'wb') as f:
            self.store.write(f)

    def close(self):
        self.sync()


class XmlStorageBackend(ConfigParserStorageBackend):
    def __init__(self, filename, *args, **kwargs):
        # Specify the name of the xml element for variables
        self.version = '1.0.0'
        self.filename = filename
        if os.path.exists(self.filename):
            with open(self.filename) as f:
                print "INFO:", "Trying to read file %s" % self.filename
                self.store = ElementTree.parse(f)
                self.version = self.store.getroot().get('version')
        else:
            # Create a basic config file with no variables
            config = ElementTree.Element('config')
            config.set('version', self.version)
            self.store = ElementTree.ElementTree(config)

        print "OPEN:", ElementTree.tostring(self.store.getroot())

        if self.version != '1.0.0':
            print "XML file is not a valid configuration version."

    def __setitem__(self, key, value):
        # If the value exists just replace it otherwise create new
        if not isinstance(key, basestring):
            raise TypeError("Key must be of string type")
        node = None
        for var in self.store.iter('var'):
            if var.find('name').text == key:
                node = var
        if node is None:
            node = ElementTree.SubElement(self.store.getroot(), 'var')
        node_name = ElementTree.SubElement(node, 'name')
        node_value = ElementTree.SubElement(node, 'value')
        node_name.text = key
        node_value.text = str(value)
        # We also will store the original type of the value
        node_value.set('type', type(value).__name__)
        print "SET:", ElementTree.tostring(self.store.getroot())
        # TODO: check the performance impact of this option
        self.sync()
        return True

    def __getitem__(self, key):
        """TODO: Still need to use 'type' attr to cast value"""
        print "GET:", ElementTree.tostring(self.store.getroot())
        for var in self.store.iter('var'):
            if var.find('name').text == key:
                return var.find('value').text or var.find('default').text
        raise KeyError("name %s was not found in xml file!" % key)

    def __delitem__(self, key):
        for var in self.store.findall('var'):
            if var.find('name').text == key:
                self.store.getroot().remove(var)
                return True
        raise KeyError("key %s was not found in config file" % key)

    def __iter__(self):
        data = {}
        for var in self.store.findall('var'):
            data[var.find('name').text] = var.find('value').text
        return iter(data)

    def __len__(self):
        return len(self.store.findall('var'))

    def close(self):
        """file never remains open so there is not need to explicitly close"""
        self.sync()

    def sync(self):
        """Write the xml data to the file with expanded subelements"""
        print "SYNC:", ElementTree.tostring(self.store.getroot())
        with open(self.filename, 'w+') as f:
            f.write(self.prettify(self.store.getroot()))
            # self.store.write(f, method='html')

    @staticmethod
    def prettify(elem):
        """Return a pretty-printed XML string for the Element."""
        rough_string = ElementTree.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t")
