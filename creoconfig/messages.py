# Levels
DEBUG = 1
INFO = 2
WARNING = 3
ERROR = 4
CRITICAL = 5


class Message(object):
    """Base class for all application generated messages"""
    def __init__(self, level, message, help=None):
        self.level = level
        self.message = message
        self._help = help

    def __eq__(self, other):
        return all(getattr(self, attr) == getattr(other, attr)
                   for attr in ['level', 'message', 'help'])

    def __str__(self):
        s = "\n\tHELP: %s" % self._help if self._help else ''
        return "%s: %s%s%s" % (level, self.message, s)

    def __repr__(self):
        return "<%s: level=%r, message=%r, help=%r>" % \
            (self.__class__.__name__, self.level, self.message, self._help)


class Debug(Message):
    def __init__(self, *args, **kwargs):
        return super(Debug, self).__init__(DEBUG, *args, **kwargs)


class Info(Message):
    def __init__(self, *args, **kwargs):
        return super(Info, self).__init__(INFO, *args, **kwargs)


class Warning(Message):
    def __init__(self, *args, **kwargs):
        return super(Warning, self).__init__(WARNING, *args, **kwargs)


class Error(Message):
    def __init__(self, *args, **kwargs):
        return super(Error, self).__init__(ERROR, *args, **kwargs)


class Critical(Message):
    def __init__(self, *args, **kwargs):
        return super(Critical, self).__init__(CRITICAL, *args, **kwargs)
