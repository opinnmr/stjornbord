import hashlib
from django.contrib.auth.hashers import SHA1PasswordHasher

# Removes the salt assertment (our passwords were salt-less to stay
# compatible with the google apps format).
#
# This is temporary, while we move over to PBKDF2PasswordHasher, and will
# eventually be removed.

class SaltlessSHA1PasswordHasher(SHA1PasswordHasher):
    def encode(self, password, salt):
        assert password
        hash = hashlib.sha1(salt + password).hexdigest()
        return "%s$%s$%s" % (self.algorithm, salt, hash)

