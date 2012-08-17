import datetime
import cPickle
import os.path
import stjornbord.settings as settings
from stjornbord.utils import prep_tmp_dir

from gdata.apps.service import AppsForYourDomainException, AppsService

TOKEN_LIFETIME = datetime.timedelta(12)
TOKEN_BASEDIR  = os.path.join(settings.GOOGLE_TMP_DIR, "tokens")
TOKEN_FILENAME = os.path.join(TOKEN_BASEDIR, "google.auth.mr")

class GoogleException(Exception): pass
 
class Google(object):
    def __init__(self):
        self.service = None

    def connect(self):
        if not self.service:
            self.service = AppsService(domain=settings.DOMAIN)
            
            try:
                prep_tmp_dir(TOKEN_BASEDIR)
                with open(TOKEN_FILENAME) as tf:
                    auth_token = cPickle.load(tf)
            except:
                auth_token = None
            
            # See if we have a valid token
            if auth_token and auth_token['timestamp'] + TOKEN_LIFETIME > datetime.datetime.now():
                self.service.SetClientLoginToken(auth_token['token'])

            # If not, log in, get the token and cache to disk
            else:
                self.service.ClientLogin(username=settings.GOOGLE_API_USER, account_type='HOSTED', service='apps', password=settings.GOOGLE_API_PASS)
                auth_token = {
                    'timestamp': datetime.datetime.now(),
                    'token':     self.service.GetClientLoginToken()
                }
                
                with open(TOKEN_FILENAME, "wb") as tf:
                    cPickle.dump(auth_token, tf)

    def list_sync(self, name, members):
        """
        Synchronizes email list to include members. If the list doesn't
        exist it's created.
        """
        self.connect()
        try:
            self.service.RetrieveEmailList(name)
        except AppsForYourDomainException, e:
            if e.error_code == 1301: #EntityDoesNotExist
                self.service.CreateEmailList(name)
            else:
                raise e

        # Get list recipients, store in a set.
        google_recipients = set( self.list_members(name) )
        local_recipients  = set( members )

        # See which entries we need to add and which should be deleted
        add_recipients = local_recipients - google_recipients
        del_recipients = google_recipients - local_recipients

        for recipient in add_recipients:
            try:
                self.service.AddRecipientToEmailList(recipient, name)
            except AppsForYourDomainException, e:
                raise GoogleException(e.reason)

        for recipient in del_recipients:
            try:
                self.service.RemoveRecipientFromEmailList(recipient, name)
            except AppsForYourDomainException, e:
                raise GoogleException(e.reason)


    def list_members(self, name):
        """
        Return list member iterable
        """
        self.connect()
        try:
            self.service.RetrieveEmailList(name)
        except AppsForYourDomainException, e:
            if e.error_code == 1301: #EntityDoesNotExist
                return
            else:
                raise e

        try:
            members = (e.title.text for e in self.service.RetrieveAllRecipients(name).entry)
        except AppsForYourDomainException, e:
            raise GoogleException(e.reason)

        return members

class FakeGoogle(object):
    def list_sync(self, name, members):
        print "FakeGoogle: list_sync"
        return

    def list_members(self, name):
        print "FakeGoogle: list_members"
        return ['fake.google.test.user1', 'fake.google.test.user2']