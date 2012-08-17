# coding: utf8

from django.db import models
from django.forms import ValidationError

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from django.contrib.admin.models import User, LogEntry
from django.utils.encoding import force_unicode
import time
import re
import datetime

from stjornbord.google.api import Google
from stjornbord import settings

ACTIVE_USER   = 1
WCLOSURE_USER = 2
INACTIVE_USER = 3
DELETED_USER  = 4

DEACTIVATE_GRACE_PERIOD = 90   # Days before deactivating a user,
                               # after marking owner as "previous"
DELETE_GRACE_PERIOD     = 365  # Days before deleting data, after
                               # deactivating a user


username_re = re.compile(r'^[a-z0-9]{1}[a-z0-9_-]{1,24}$')

def validate_username(username, current_holder=None):
    """
    Check for username validity and availability. If a "current holder" is
    supplied, that object will be excluded from the availability check.
    """
    if not username_re.search(username):
        raise ValidationError(u"Notendanöfn meiga einungis innihalda enska bókstafi, tölustafi og undirstrik.")

    users           = []
    for u in User.objects.filter(username=username):
        if current_holder is None or (current_holder is not None and u != current_holder.user):
            users.append(u.get_profile())
    
    mailinglists    = MailingList.objects.filter(username=username)
    reserved        = ReserverdUsername.objects.filter(username=username)

    for qs in (users, mailinglists, reserved):
        if len(qs) != 0 and qs[0] != current_holder:
            raise ValidationError(u"Notendanafn ekki laust")

def send_email(username, full_name, deactivate):
    if settings.DEBUG:
        log_wrapper(None, "NOT SENDING EMAIL TO %s@mr.is" % username)
    else:        
        log_wrapper(None, "Sending email to %s@mr.is" % username)
        from django.core.mail import EmailMessage
        from django.template import loader, Context

        email_template  = loader.get_template('user/deactivate.txt')
        date_format     = deactivate.strftime("%d %b")
        context = Context({
                    'name': full_name,
                    'days': DEACTIVATE_GRACE_PERIOD,
                    'date': date_format,
                    })

        email = EmailMessage(
                    u"Lokað verður á MR netfang þitt %s" % date_format,
                    email_template.render(context),
                    u'Kerfisstjórn MR <hjalp@mr.is>',   # from
                    ["%s@mr.is" % username],       # to
                    ['hjalp@mr.is'],                 # bcc
                )
        email.send()
    

class UserStatus(models.Model):
    name = models.CharField(max_length=40)
    active = models.BooleanField()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "User Status"
        verbose_name_plural = "User statuses"

class ReserverdUsername(models.Model):
    username        = models.CharField(max_length=40)

    def __unicode__(self):
        return self.username
    
    def save(self):
        # Force username validation. See User's comments
        validate_username(self.username, self)
        models.Model.save(self)

class PosixGroup(models.Model):
    name        = models.CharField(max_length=40)
    posix_gid   = models.IntegerField()
    
    def __unicode__(self):
        return self.name

class PosixUidPool(models.Model):
    user_type       = models.ForeignKey(ContentType, primary_key=True)
    next_uid        = models.IntegerField()
    
    def get_and_increment(self):
        uid = self.next_uid
        self.next_uid += 1
        self.save()
        return uid
    
    def __unicode__(self):
        return self.user_type.name

class OldUser(models.Model):
    username        = models.CharField(max_length=128, blank=True)
    password        = models.CharField(max_length=128, blank=True)
    status          = models.ForeignKey(UserStatus)
    deactivate      = models.DateField(blank=True, null=True, help_text="Einungis ef notandi bíður lokunar")
    purge           = models.DateField(blank=True, null=True, help_text="Einungis ef notandi bíður gagnaeyðslu")

    user_type       = models.ForeignKey(ContentType)
    kennitala       = models.CharField(max_length=10)
    content_object  = generic.GenericForeignKey(ct_field="user_type", fk_field="kennitala")

    class Meta:
        db_table = 'user_user'

class UserProfile(models.Model):
    user            = models.ForeignKey(User, unique=True)
    status          = models.ForeignKey(UserStatus)
    deactivate      = models.DateField(blank=True, null=True, help_text="Einungis ef notandi bíður lokunar")
    purge           = models.DateField(blank=True, null=True, help_text="Einungis ef notandi bíður gagnaeyðslu")

    user_type       = models.ForeignKey(ContentType)
    kennitala       = models.CharField(max_length=10)
    content_object  = generic.GenericForeignKey(ct_field="user_type", fk_field="kennitala")

    dirty           = models.IntegerField(blank=True, null=True, db_index=True, help_text="Einungis ef notandi bíður uppfærslu")
    
    posix_uid       = models.IntegerField(unique=True, blank=True)
    posix_groups    = models.ManyToManyField(PosixGroup, blank=True)

    tmppass         = models.CharField(max_length=80, blank=True)
    inipa           = models.IntegerField(blank=True, default=0)

    def set_password(self, raw_password):
        # Set password for Django's auth user model, without a salt.
        import hashlib
        self.user.password = u"sha1$$%s" % hashlib.sha1(raw_password.encode("utf8")).hexdigest()
        self.user.save()
        
        # Temporarily store password in clear text, for FreeIPA
        self.tmppass = raw_password
        self.set_dirty()

    def get_password(self):
        # Get sha1 password, without the sha1$$ prefix. Fails if we
        # get a password with a salt.
        p = self.user.password
        if not p.startswith("sha1$$"):
            raise RuntimeException("Wow, this password is not sha1 without a salt! (%s)" % p[p.rindex("$"):])
        return p.split("$", 2)[2]

    def get_absolute_url(self):
        return "%s%s/" % (self.content_object.get_absolute_url(), self.id)
    
    def set_dirty(self):
        self.dirty = time.time()

    def set_deactivate(self):
        self.deactivate = datetime.date.today() + datetime.timedelta(DEACTIVATE_GRACE_PERIOD)

    def unset_deactivate(self):
        self.deactivate = None

    def set_purge(self):
        self.purge = datetime.date.today() + datetime.timedelta(DELETE_GRACE_PERIOD)

    def unset_purge(self):
        self.purge = None

    def save(self):
        # Yes, we are running this twice, both as an admin validator and
        # here in save(). The form validator is only called when used within
        # the django administrator (not normal functionality) but can be
        # avoided when using the normal model-api. Therefore we force a validation
        # then the model is being saved.
        validate_username(self.user.username, self)
        
        # There may be a better way of seeing whether a variable has
        # changed or not - I couldn't find one quickly. Overloading
        # __init__ doesn't solve it.
        try:
            prev_version = self.__class__.objects.get(pk=self.pk)
        except self.DoesNotExist:
            prev_version = None

        # Temporarily set all users as dirty on any change
        self.set_dirty()

        # Assign POSIX user id, based on user type
        if not self.posix_uid:
            self.posix_uid = PosixUidPool.objects.get(pk=self.user_type).get_and_increment()
            self.set_dirty()

        if prev_version is None:
            # Daemon will create the user
            self.set_dirty()
        else:
            prev_status = int(prev_version.status_id)
            cur_status  = int(self.status_id)
            
            # Active user given the a deactivation notice
            if (prev_status == ACTIVE_USER and cur_status == WCLOSURE_USER):
                self.set_deactivate()
                send_email(self.user.username, self.content_object.get_fullname(), self.deactivate)
            
            # User being deactivated
            elif (prev_status == WCLOSURE_USER and cur_status == INACTIVE_USER):
                self.unset_deactivate()
                self.set_purge()

                # Daemon will suspend/disable the user
                self.set_dirty()

            # User data being deleted or archived
            elif (prev_status == INACTIVE_USER and cur_status == DELETED_USER):
                self.unset_purge()

                # Daemon will delete user data
                self.set_dirty()

            # Removing the awaiting closure status.
            elif (prev_status == WCLOSURE_USER and cur_status == ACTIVE_USER):
                self.unset_deactivate()

            # Reactivating a suspended user
            elif (prev_status == INACTIVE_USER and cur_status == ACTIVE_USER):
                self.unset_deactivate() # Shouldn't be set anyway
                self.unset_purge()

                # Daemon will activate the user
                self.set_dirty()

            # Reactivating a deleted user
            elif (prev_status == DELETED_USER and cur_status == ACTIVE_USER):
                # Daemon will activate the user
                self.set_dirty()

            # Invalid move, cannot move from inactive to awaiting closure.
            elif (prev_status == INACTIVE_USER and cur_status == WCLOSURE_USER):
                raise Exception("Sorry, changing state from Inactive to waiting for closure is not allowed. Activate the user instead.")

        # Finally, save the user
        models.Model.save(self)

    def delete(self):
        """
        We don't want to allow Users to be deleted!
        """
        # TODO: Should we purge the pykota entry?
        
        raise Exception("Sorry, users may not be deleted! Change it's status instead.")

    def __unicode__(self):
        return self.user.username


class MailingList(models.Model):
    """
    Mailinglist object, keeps record of list name and owner, but not
    recipients - they are only stored with Google as of now.
    """
    username        = models.CharField(max_length=40)

    user_type       = models.ForeignKey(ContentType)
    kennitala       = models.CharField(max_length=10)
    content_object  = generic.GenericForeignKey(ct_field="user_type", fk_field="kennitala")

    def __unicode__(self):
        return self.username

    def get_absolute_url(self):
        return "%smailinglist/%s/" % (self.content_object.get_absolute_url(), self.id)

    def save(self):
        # Force username validation. See User's comments
        validate_username(self.username, self)
        models.Model.save(self)


def log_wrapper(obj, message, action=None):
    # TODO: Use Django's new logging mechanism when updating
    # to new Django release.
    if settings.DEBUG:
        print "LOG:", message