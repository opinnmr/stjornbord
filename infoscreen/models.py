from django.db import models
from stjornbord.ou.models import OrganizationalUnit
import datetime

class Announcement(models.Model):
    title       = models.CharField(max_length=100)
    visible     = models.BooleanField(default=True)
    signature   = models.CharField(max_length=40)
    body        = models.TextField()
    duration    = models.IntegerField(default=10)
    date        = models.DateTimeField(default=datetime.datetime.now())

    def __unicode__(self):
        return self.title
        
    class Meta:
        ordering = ['date']


class AbsentEmployees(models.Model):
    date        = models.DateField(default=datetime.date.today(), unique=True)
    employees   = models.ManyToManyField(OrganizationalUnit, through="AbsentRelation", limit_choices_to={'status__id': 2})

    def __unicode__(self):
        return unicode(self.date)

    class Meta:
        ordering = ['-date']


class AbsentRelation(models.Model):
    day     = models.ForeignKey(AbsentEmployees)
    employee= models.ForeignKey(OrganizationalUnit)
    subject = models.CharField(max_length=40, blank=True)