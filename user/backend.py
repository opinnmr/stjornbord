from django.contrib.auth.backends import ModelBackend
from stjornbord.settings import DOMAIN

TRIM_DOMAIN = "@%s" % DOMAIN

class TrimDomainBackend(ModelBackend):
    """
    Trim settings.DOMAIN from the username field, if supplied
    """
    def authenticate(self, username=None, password=None):
        if username.endswith(TRIM_DOMAIN):
            username = username[:-len(TRIM_DOMAIN)]
        return ModelBackend.authenticate(self, username, password)
