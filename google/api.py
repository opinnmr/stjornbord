import datetime
import cPickle
import os.path
import stjornbord.settings as settings
from stjornbord.utils import prep_tmp_dir

from gdata.apps.service import AppsForYourDomainException, AppsService

TOKEN_LIFETIME = datetime.timedelta(12)
TOKEN_BASEDIR = os.path.join(settings.GOOGLE_TMP_DIR, "tokens")
TOKEN_FILENAME = os.path.join(TOKEN_BASEDIR, "google.auth.mr")

def recode(s):
    if type(s) is unicode:
        return s.encode("utf8")
    return s

def recode_user(user):
     user.name.family_name = recode(user.name.family_name)
     user.name.given_name  = recode(user.name.given_name)
     return user

class GoogleException(Exception): pass
 
class Google(object):
    def __init__(self):
        self.service = None

    def connect(self):
        if not self.service:
            self.service = AppsService(domain='mr.is')
            
            try:
                prep_tmp_dir(TOKEN_BASEDIR)
                tf = open(TOKEN_FILENAME)
                auth_token = cPickle.load(tf)
                tf.close()
            except:
                auth_token = None
            
            # See if we have a valid token
            if auth_token and auth_token['timestamp'] + TOKEN_LIFETIME > datetime.datetime.now():
                self.service.SetClientLoginToken(auth_token['token'])

            # If not, log in, get the token and cache to disk
            else:
                self.service.ClientLogin(username=settings.GOOGLE_API_USER, account_type='HOSTED', service='apps', password=settings.GOGGLE_API_PASS)
                auth_token = {
                    'timestamp': datetime.datetime.now(),
                    'token':     self.service.GetClientLoginToken()
                }
                
                tf = open(TOKEN_FILENAME, "wb")
                cPickle.dump(auth_token, tf)
                tf.close()


    def user_create(self, username, first_name, last_name, password):
        self.connect()
        
        if not password:
            # temporary mix, as we need to be able to create invalid users
            # while transferring over
            import hashlib, random
            password = hashlib.sha1(str(random.random())).hexdigest()

        try:
            user = self.service.CreateUser(
                user_name              = username,
                family_name            = recode(last_name),
                given_name             = recode(first_name),
                password               = password,
                password_hash_function = "SHA-1"
                )
        except AppsForYourDomainException, e:
            raise GoogleException(e.reason)
        
        return user


    def user_get(self, username):
        self.connect()

        try:
            user = self.service.RetrieveUser(username)
        except AppsForYourDomainException, e:
            raise GoogleException(e.reason)

        return user


    def user_get_usernames(self):
        self.connect()
        try:
            all_users = self.service.RetrieveAllUsers().entry
        except AppsForYourDomainException, e:
            raise GoogleException(e.reason)

        for username in all_users:
            yield username.title.text
    
    def user_update(self, username, user):
        self.connect()
        try:
            self.service.UpdateUser(username, recode_user(user))
        except AppsForYourDomainException, e:
            raise GoogleException(e.reason)

    def user_delete(self, username):
        # User deletion disabled for now
        raise Exception("We don't delete users at the moment!")

        #self.connect()
        #try:
        #    pass
        #    #self.service.DeleteUser(username)
        #except AppsForYourDomainException, e:
        #    raise GoogleException(e.reason)

    def user_update_password(self, username, sha1_password):
        user = self.user_get(username)
        user.login.password           = sha1_password
        user.login.hash_function_name = 'SHA-1'
        self.user_update(username, user)

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
    def user_create(self, *args, **kwargs):
        print "FakeGoogle: user_create"
        return

    def user_get(self, username):
        print "FakeGoogle: user_get"
        return "test.user"

    def user_get_usernames(self):
        print "FakeGoogle: user_get_usernames"
        return ['fake.google.test.user1', 'fake.google.test.user2']

    def user_update(self, username, user):
        print "FakeGoogle: user_update"
        return
        
    def user_delete(self, username):
        print "FakeGoogle: user_delete"
        return
        
    def user_update_password(self, username, sha1_password):
        print "FakeGoogle: user_update_password"
        return
        
    def list_sync(self, name, members):
        print "FakeGoogle: list_sync"
        return

    def list_members(self, name):
        print "FakeGoogle: list_members"
        return ['fake.google.test.user1', 'fake.google.test.user2']

#if not settings.UPDATE_GOOGLE:
#    Google = FakeGoogle
