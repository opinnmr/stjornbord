from django.db import models
from django.contrib.contenttypes import generic

from stjornbord.ou.models import Status, update_associated_users
from stjornbord.user.models import UserProfile

class Klass(models.Model):
    name        = models.CharField(max_length=5)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Class"
        verbose_name_plural = "Classes"

class LegalGuardian(models.Model):
    email   = models.EmailField(max_length=100)

    def __unicode__(self):
        return self.email

class Student(models.Model):
    kennitala  = models.CharField(primary_key=True, unique=True, max_length=10)
    first_name = models.CharField(max_length=40)
    last_name  = models.CharField(max_length=40)
    status     = models.ForeignKey(Status)
    klass      = models.ForeignKey(Klass, related_name="students")
    guardians  = models.ManyToManyField(LegalGuardian)
    
    userp       = generic.GenericRelation(UserProfile, content_type_field="user_type", object_id_field="kennitala")

    def delete(self):
        """
        We don't want to allow Students to be deleted!
        """
        raise Exception("Sorry, students may not be deleted! Change the student's status instead.")

    def get_absolute_url(self):
        return "/students/%s/" % self.kennitala

    def get_fullname(self):
        """
        Returns the student's full name
        """
        return self.first_name +' '+ self.last_name

    def save(self):
        """
        Disable my users if I'm moving from an open state to a closed one
        """
        update_associated_users(self)
        models.Model.save(self)
            
    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)

    class Meta:
        ordering = ['first_name', 'last_name']

