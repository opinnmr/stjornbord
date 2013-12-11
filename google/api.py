import oauth2client.client
import oauth2client.file
from apiclient.discovery import build
from apiclient import errors
import httplib2
import logging

log = logging.getLogger("stjornbord.api.google")

# TODO: push to own package, share with stjornbord-update-daemon

class GoogleAPIException(Exception): pass
class GoogleAPICredentialException(GoogleAPIException): pass

def catch_api_exceptions(func):
    """
    Wrapper to catch API exceptions. Logs and wraps in a GoogleAPIException
    to make life easier for the caller.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except oauth2client.client.AccessTokenRefreshError:
            raise GoogleAPICredentialException()

        except GoogleAPICredentialException:
            raise

        except errors.Error, e:
            log.exception("Uncaught exception in %s", func.__name__)
            raise GoogleAPIException()

    return wrapper


class Google(object):
    def __init__(self, token_storage, domain):
        self.token_storage = token_storage
        self.domain = domain

        self._service = None


    @property
    def service(self):
        if self._service is None:
            credentials = self._get_credentials()

            # Build client
            http = credentials.authorize(http = httplib2.Http())
            self._service = build("admin", "directory_v1", http=http)

        return self._service


    def _get_storage(self):
        return oauth2client.file.Storage(self.token_storage)


    def _get_credentials(self):
        credentials = self._get_storage().get()

        if credentials is None or credentials.invalid:
            raise GoogleAPICredentialException()

        return credentials


    @catch_api_exceptions
    def list_sync(self, name, members):
        """
        Synchronizes email list to include members. If the list doesn't
        exist it's created.
        """

        list_email = "%s@%s" % (name, self.domain)
        log.debug("Updating membership of %s", list_email)

        try:
            self.service.groups().get(groupKey=list_email).execute()
        except errors.HttpError, e:
            if e.resp.status == 404:
                # List does not exist, create it!
                log.info("Creating list %s as part of list_sync", list_email)
                self.service.groups().insert(email=list_email).execute()
            else:
                raise

        # Get list recipients, store in a set.
        google_recipients = set( self.list_members(name) )
        local_recipients  = set( members )

        # See which entries we need to add and which should be deleted
        add_recipients = local_recipients - google_recipients
        del_recipients = google_recipients - local_recipients

        for recipient in add_recipients:
            log.info("Adding recipient %s to %s", recipient, list_email)
            self.service.members().insert(groupKey=list_email,
                body={"email": recipient}).execute()

        for recipient in del_recipients:
            log.info("Removing recipient %s to %s", recipient, list_email)
            self.service.members().delete(groupKey=list_email,
                memberKey=recipient).execute()


    @catch_api_exceptions
    def list_members(self, name):
        """
        Return the list member's email addresses.

        Returns None if the list does not exist.
        """

        list_email = "%s@%s" % (name, self.domain)
        log.debug("Listing recipients of %s", list_email)

        emails = []
        try:
            request = self.service.members().list(groupKey=list_email)
            while request is not None:
                result = request.execute()

                if "members" in result:
                    for member in result["members"]:
                        emails.append(member["email"])

                request = self.service.members().list_next(request, result)

        except errors.HttpError, e:
            if e.resp.status == 404:
                # List does not exist, return empty list
                return None
            raise e


        return emails


    def authenticate(self, client_secrets, scope):
        """
        Helper function to establish the google authentication. Not strictly
        a part of the API. Since this API is for an installed application and
        the end user may not have access to authenticate the API usage, we
        generally just return a GoogleAPICredentialException if we can't
        authenticate. The operator is expected to establish the Google authentication
        and maintain it (i.e. if the refresh token expires or is revoked).
        """
        flow = oauth2client.client.flow_from_clientsecrets(client_secrets, scope=scope)
        flow.redirect_uri = oauth2client.client.OOB_CALLBACK_URN

        print
        print "This will guide you through the oauth2 process. Please"
        print "open the following URL in your browser and follow the on-screen"
        print "instructions to obtain a verification code. Once you do, please"
        print "enter the obtained code below."
        print
        print "Important: make sure to run this as whatever user will use the"
        print "refresh tokens."
        print
        print flow.step1_get_authorize_url()
        print
        print
        code = raw_input("Please enter verification code: ").strip()

        try:
            credential = flow.step2_exchange(code)
        except oauth2client.client.FlowExchangeError, e:
            sys.exit('Authentication has failed: %s' % e)

        storage = self._get_storage()
        storage.put(credential)
        credential.set_store(storage)

        print 'Authentication successful.'
