from django.contrib.auth.backends import ModelBackend
from stjornbord.user.models import UserProfile
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

        # If this user has a profile, make sure we only authenticate
        # active users
        try:
            if user and user.get_profile().status.active:
                return user
        except UserProfile.DoesNotExist:
            # This user doesn't have a profile, so we'll allow him
            # through
            return user

        return None