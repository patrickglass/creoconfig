import time
import hmac
import base64
import hashlib
import calendar

from exceptions import SignatureError


class Signer(object):
    """
    This class implements basic value verification using hmac.
    It is able to detect modification of a text value outside of the program.
    This is meant to allow one to capture the datetime of the stored value and
    not be cryptographically secure. A malitious user would be able to re-create
    the signed value if they have access to this source.
    """
    def __init__(self, key=None, salt=None):
        self._key = key
        self._salt = salt or 'creoconfig.signing'
        self._separator = '::'
        # self._skip_validation = skip_validation

    def sign(self, value, salt=None):
        """
        creates a complext text string which has the human readable value
        as well as a timestamp and hash signature. This can be used to
        detect tampering
        """
        sig = self._get_signature(value, salt)
        return str(value) + self._separator + str(sig)

    def unsign(self, value, salt=None, validate=True):
        """
        extracts the value from the complex text field.

        value format is:
            orig_value + SEP + SIGNATURE
        """
        # extract the complex field
        val, sig = value.rsplit(self._separator, 1)

        # Check that we have a valid signature
        if validate and not self.validate(val, sig):
            raise SignatureError("Could not validate signature of field")
        return val

    def validate(self, value, signature, salt=None):
        salt = salt or self._salt
        gensig = self._get_signature(value, salt=salt)
        print("INFO: Comparing Signatures: %s =? %s" % (signature, gensig))
        if not self.compare_digest(self.to_bytes(gensig), self.to_bytes(signature)):
            return False
        return True

    def _get_signature(self, value, salt=None):
        """
        creates a complext text string which has the human readable value
        as well as a timestamp and hash signature. This can be used to
        detect tampering
        """
        h = hashlib.sha1()
        h.update(self.to_bytes(salt or self._salt))
        h.update(self.to_bytes(self._key))
        sig = hmac.new(h.digest(), value, digestmod=hashlib.sha1).digest()
        return base64.encodestring(sig)

    @staticmethod
    def to_bytes(value):
        return bytes(value)

    @staticmethod
    def compare_digest(x, y):
        return x == y
        if not (isinstance(x, bytes) and isinstance(y, bytes)):
            raise TypeError("both inputs should be instances of bytes")
        if len(x) != len(y):
            return False
        result = 0
        for a, b in zip(x, y):
            result |= a ^ b
        return result == 0


class TimestampSigner(Signer):
    """
    This class implements basic value verification using hmac.
    It is able to detect modification of a text value outside of the program.
    This is meant to allow one to capture the datetime of the stored value and
    not be cryptographically secure. A malitious user would be able to re-create
    the signed value if they have access to this source.
    """
    def sign(self, value, salt=None, timestamp=None):
        """
        creates a complext text string which has the human readable value
        as well as a timestamp and hash signature. This can be used to
        detect tampering
        """
        value = str(value)
        value += self._separator + TimestampSigner.encode_timestamp(timestamp)
        return super(TimestampSigner, self).sign(value, salt)

    def unsign(self, value, salt=None):
        """
        extracts the value and timestamp from the complex text field.

        value format is:
            orig_value + SEP + TIMESTAMP_HASH + SEP + SIGNATURE
        """
        print "DEBUG: " + value
        value_time = super(TimestampSigner, self).unsign(value, salt)
        data = value_time.rsplit(self._separator, 1)
        if len(data) == 2:
            data[1] = self.decode_timestamp(data[1])
        return data

    @staticmethod
    def encode_timestamp(timestamp=None):
        # t = time.time()
        t = calendar.timegm(time.gmtime(timestamp))
        return base64.b64encode(bytes(t))

    @staticmethod
    def decode_timestamp(value):
        return float(base64.b64decode(value))


