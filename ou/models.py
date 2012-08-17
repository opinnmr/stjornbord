from django.db import models
from django.contrib.contenttypes import generic

from stjornbord.user.models import UserProfile, MailingList, log_wrapper, ACTIVE_USER, WCLOSURE_USER

class Status(models.Model):
    name   = models.CharField(max_length=40)
    active = models.BooleanField()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Status"
        verbose_name_plural = "Statuses"


class Group(models.Model):
    name   = models.CharField(max_length=40)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Organizational Group"
        verbose_name_plural = "Organizational Groups"


class OrganizationalUnit(models.Model):
    kennitala   = models.CharField(primary_key=True, max_length=10)
    first_name  = models.CharField(max_length=40)
    last_name   = models.CharField(max_length=40)
    status      = models.ForeignKey(Status)
    group       = models.ForeignKey(Group)

    userp       = generic.GenericRelation(UserProfile, content_type_field="user_type", object_id_field="kennitala")
    mailinglist = generic.GenericRelation(MailingList, content_type_field="user_type", object_id_field="kennitala")

    def save(self):
        """
        Disable my users if I'm moving from an open state to a closed one
        """
        update_associated_users(self)
        models.Model.save(self)

    def delete(self):
        """
        We don't allow Employees to be deleted!
        """
        raise Exception("Sorry, employees may not be deleted! Change the employee's status instead.")

    def get_absolute_url(self):
        return "/ou/%s/" % self.kennitala

    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)

    def get_fullname(self):
        """
        Returns the employee's full name
        """
        return self.first_name +' '+ self.last_name

    class Meta:
        ordering = ['first_name', 'last_name']

def update_associated_users(newme):
    """
    This is a helper function used by Student and OrganizationalUnit models.
    It looks to see if the "human" is being moved from an active status to an
    inactive status. If so, locate possible users connected with the person
    and mark them as waiting for closure. The User model will deal with
    sending out an email to the user and all that.
    
    If the user is moving from an inactive state to an active state, and has
    users which are awaiting closure, those user accounts are reactivated.
    
    TODO: Currently, disabled/deleted users are not recreated. We may want
    to re-enable disabled users.
    """
    try:
        oldme = newme.__class__.objects.get(pk=newme.pk)
    except newme.DoesNotExist:
        oldme = None
    else:
        if int(oldme.status_id) != int(newme.status_id):
    
            # Ok, seems as the status_id has changed. Is the human being
            # moved from an inactive state to an active state?
            if newme.status.active and not oldme.status.active:
                # Yes, that is the case. Let's loop through the human's users
                # and reactivate those marked waiting for closure. We don't
                # reactivate inactive user accounts, that needs to be done
                # manually (we don't want to get too smart for our own good)
                #
                # This is mainly thought of for humans who got the "your account
                # is being closed" email but for some reason should keep their
                # accounts. They might be exchange students abroad or whatever..
                for userp in newme.userp.filter(status=WCLOSURE_USER):
                    userp.status_id = ACTIVE_USER
                    userp.save()
            
            # Is the human being moved from an active state to an inactive one ?
            elif oldme.status.active and not newme.status.active:
                log_wrapper(newme, "State changed to inactive. Disabling active users.")

                # Yes, that seems to be the case. Find all the persons users
                # and mark them as waiting for closure
                for userp in newme.userp.all():
                    if userp.status.active:
                        userp.status_id = WCLOSURE_USER
                        userp.save()