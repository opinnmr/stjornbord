import os
import logging

from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.http import HttpResponseForbidden
from stjornbord import settings
from stjornbord_google_api import Google, GoogleAPICredentialException

log = logging.getLogger("stjornbord")


def mrnet_only(func):
    """
    A decorator that checks to see if the current request is from the
    server's network. If not, an error page is displayed.
    """
    def validate_request(request, *args, **kwargs):
        if request.META['REMOTE_ADDR'] == settings.MRNET_IP or settings.DEBUG:
            return func(request, *args, **kwargs)
        else:
            return render_to_response(
                'registration/mrnet_only.html', {},
                context_instance=RequestContext(request))

    return validate_request

def verify_sync_secret(func):
    """
    A decorator that verifies the SYNC_SECRET is correct, used
    to protect sensitive views intended for user/device/passowrd
    synchronization
    """
    
    def validate_request(request, *args, **kwargs):
        if request.POST.get('secret', None) == settings.SYNC_SECRET:
            return func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Invalid SYNC_SECRET.")

    return validate_request

def prep_tmp_dir(path):
    if os.path.isdir(path):
        return
    return os.makedirs(path)


def create_google_api():
    """
    Create a Google API instance, don't cache or share for now (httplib2
    is not thread-safe).
    """
    return Google(settings.GOOGLE_TOKEN, settings.DOMAIN)


def handle_google_auth_exception(func):

    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)

        except GoogleAPICredentialException:
            log.fatal("Google authentication failed. "
                "Please manually re-authenticate Stjornbord towards Google.")

            return render(request, 'googlecreds.html',
                context_instance=RequestContext(request), status=500)

    return wrapper
