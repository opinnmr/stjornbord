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
import logging

log = logging.getLogger("stjornbord")

from stjornbord.utils import create_google_api
from stjornbord import settings

ACTIVE_USER   = 1
WCLOSURE_USER = 2
INACTIVE_USER = 3
DELETED_USER  = 4

DEACTIVATE_GRACE_PERIOD = 90   # Days before deactivating a user,
                               # after marking owner as departed
DELETE_GRACE_PERIOD     = 365  # Days before deleting data, after
                               # deactivating a user


class InvalidUserProfileStateChangeException(Exception): pass

username_re = re.compile(r'^[a-z0-9]{1}[a-z0-9_-]{1,24}$')

def validate_username(username, current_holder=None):
    """
    Check for username validity and availability. If a "current holder" is
    supplied, that object will be excluded from the availability check.
    """
    if not username_re.search(username):
        raise ValidationError(u"Notendanöfn meiga einungis innihalda enska bókstafi, tölustafi og undirstrik.")

    users = []
    for u in User.objects.filter(username=username):
        if current_holder is None or (current_holder is not None and u != current_holder.user):
            users.append(u.get_profile())
    
    mailinglists    = MailingList.objects.filter(username=username)
    reserved        = ReserverdUsername.objects.filter(username=username)

    for qs in (users, mailinglists, reserved):
        if len(qs) != 0 and qs[0] != current_holder:
            raise ValidationError(u"Notendanafn ekki laust")

def send_deactivate_email(username, full_name, deactivate, reminder=False):
    log.info("Sending email to %s@mr.is", username)
    from django.core.mail import EmailMessage
    from django.template import loader, Context

    email_template  = loader.get_template('user/deactivate.txt')
    date_format     = deactivate.strftime("%d %b")
    context = Context({
                'name': full_name,
                'days': (deactivate - datetime.date.today()).days,
                'date': date_format,
                })

    subject = u"Lokað verður á MR netfang þitt %s" % date_format
    if reminder:
        subject = u"Áminning: %s" % subject

    email = EmailMessage(
                subject,
                email_template.render(context),
                u'Kerfisstjórn MR <hjalp@mr.is>', # from
                ["%s@mr.is" % username],          # to
                ['hjalp@mr.is'],                  # bcc
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
    
    def save(self, *args, **kwargs):
        # Force username validation. See User's comments
        validate_username(self.username, self)
        models.Model.save(self, *args, **kwargs)

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

class UserProfile(models.Model):
    user            = models.ForeignKey(User, unique=True)
    status          = models.ForeignKey(UserStatus)
    deactivate      = models.DateField(blank=True, null=True, help_text="Einungis ef notandi bíður lokunar")
    purge           = models.DateField(blank=True, null=True, help_text="Einungis ef notandi bíður gagnaeyðslu")

    user_type       = models.ForeignKey(ContentType)
    kennitala       = models.CharField(max_length=10)
    content_object  = generic.GenericForeignKey(ct_field="user_type", fk_field="kennitala")

    dirty           = models.IntegerField(blank=True, null=True, db_index=True, help_text="Einungis ef notandi bíður uppfærslu")
    tmppass         = models.CharField(max_length=80, blank=True)
    
    posix_uid       = models.IntegerField(unique=True, blank=True)
    posix_groups    = models.ManyToManyField(PosixGroup, blank=True)


    def set_password(self, raw_password):
        # Update password on the django side.
        self.user.set_password(raw_password)
        self.user.save()
        
        # Temporarily store password in clear text, for authentication
        # backend. For Google Apps, we can use sha1, but for FreeIPA we
        # need to store the password in clear-text. This is read by the
        # update daemon and cleared with the dirty bit.
        self.tmppass = raw_password
        self.set_dirty()

    def get_absolute_url(self):
        return "%s%s/" % (self.content_object.get_absolute_url(), self.id)
    
    def set_dirty(self):
        self.dirty = time.time()
        
    def clear_dirty(self, timestamp):
        from django.db import connection, transaction
        cursor = connection.cursor()
        cursor.execute("UPDATE user_userprofile SET dirty = 0, tmppass = '' WHERE id = %s AND dirty = %s", (self.id, timestamp))
        transaction.commit_unless_managed()

    def set_deactivate(self):
        self.deactivate = datetime.date.today() + datetime.timedelta(DEACTIVATE_GRACE_PERIOD)

    def unset_deactivate(self):
        self.deactivate = None

    def set_purge(self):
        self.purge = datetime.date.today() + datetime.timedelta(DELETE_GRACE_PERIOD)

    def unset_purge(self):
        self.purge = None

    def save(self, *args, **kwargs):
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
            
            # No state change
            if prev_status == cur_status:
                pass

            # Active user given the a deactivation notice
            elif (prev_status == ACTIVE_USER and cur_status == WCLOSURE_USER):
                self.set_deactivate()
                send_deactivate_email(self.user.username, self.content_object.get_fullname(), self.deactivate)
            
            # User being deactivated
            elif (prev_status in (ACTIVE_USER, WCLOSURE_USER) and cur_status == INACTIVE_USER):
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
                raise InvalidUserProfileStateChangeException("Sorry, changing state from Inactive to waiting for closure is not allowed. Activate the user instead.")

            else:
                log.fatal("Invalid state change (from %s to %s)", prev_status, cur_status)
                raise InvalidUserProfileStateChangeException("Invalid state change (from %s to %s)" % (prev_status, cur_status))

        # Finally, save the user
        models.Model.save(self, *args, **kwargs)
        
    def delete(self):
        """
        We don't want to allow Users to be deleted!
        """
        # TODO: Should we purge the pykota entry?
        
        raise Exception("Sorry, users may not be deleted! Change it's status instead.")

    def __unicode__(self):
        return self.user.username

# TODO: This should probably be moved to it's own module. Currently calls the
# Google api directly, but could be abstracted for other backends.
class MailingList(models.Model):
    """
    Base mailinglist object. Keeps record of the list name and owner, but
    not its members. That's handled by one of the
    """
    username        = models.CharField(max_length=40)

    user_type       = models.ForeignKey(ContentType)
    kennitala       = models.CharField(max_length=10)
    content_object  = generic.GenericForeignKey(ct_field="user_type", fk_field="kennitala")

    _members_dirty  = False
    _members        = None

    def __unicode__(self):
        return self.username

    def get_absolute_url(self):
        return "%smailinglist/%s/" % (self.content_object.get_absolute_url(), self.id)

    def save(self, *args, **kwargs):
        # Force username validation. See User's comments
        validate_username(self.username, self)

        # Implemented by 
        self._sync_members()
        models.Model.save(self, *args, **kwargs)

    # The following three functions are specific to Google Apps. These can
    # be factored out if we later want to support more mailing list backends.

    def get_members(self):
        if self._members is None:
            self._members = create_google_api().list_members(self.username)
        return self._members

    def set_members(self, members):
        self._members = members
        self._members_dirty = True

    def _sync_members(self):
        if self._members_dirty:
            create_google_api().list_sync(self.username, self._members)