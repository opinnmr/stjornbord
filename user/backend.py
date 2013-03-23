from django.contrib.auth.backends import ModelBackend
from stjornbord.settings import DOMAIN

TRIM_DOMAIN = "@%s" % DOMAIN

class StjornbordBackend(ModelBackend):
    """
    Only authenticate active users. Also trim settings.DOMAIN from the
    username field, if supplied.
    """
    def authenticate(self, username=None, password=None):
        if username.endswith(TRIM_DOMAIN):
            username = username[:-len(TRIM_DOMAIN)]

        user = ModelBackend.authenticate(self, username, password)

        if user:
            # Always authenticate a superuser (even if he hasn't got a
            # profile)
            if user.is_superuser:
                return user

            # Only authenticate users that are active or waiting for
            # closure.
            if user.get_profile().status.active:
                return user

        return None