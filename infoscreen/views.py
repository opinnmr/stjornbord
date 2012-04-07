#coding: utf8
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.template import RequestContext
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_list
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render_to_response
from django.http import HttpResponse
import simplejson
import datetime

from stjornbord.infoscreen.models import Announcement, AbsentEmployees

def screen(request):
    return direct_to_template(request, 'infoscreen/screen.html')


def _get_todays_absent_employees():
    """
    Returns iterable of absent employees. In case no employees
    are absent, returns empty list.
    """
    try:
        today = AbsentEmployees.objects.get(date=datetime.date.today())
    except AbsentEmployees.DoesNotExist:
        return []

    return today.absentrelation_set.order_by('employee')    


def json(request):
    """
    Returns JSON encoded list of announcements and absent
    employees.
    """
    announcements = []
    absent = []

    for a in Announcement.objects.filter(visible=True):
        announcements.append({
            'title':        a.title,
            'signature':    a.signature,
            'body':         a.body,
            'duration':     a.duration,
        })

    for e in _get_todays_absent_employees():
        absent.append({
            'employee':   e.employee.get_fullname(),
            'subject':    e.subject,
        })

    context = {
        'announcements': announcements,
        'absent': absent,
    }

    response = HttpResponse(mimetype="application/json")
    simplejson.dump(context, response)
    return response


class AbsentEmployesRss(Feed):
    """
    Prepares RSS feed of absent employees
    """
    title = u"Forföll starfsmanna"
    link = "http://www.mr.is"
    description = u"Forföll starfsmanna Menntaskólans."

    def items(self):
        return _get_todays_absent_employees()

    def item_title(self, item):
        return item.employee.get_fullname()

    def item_description(self, item):
        return item.subject
    
    def item_link(self, item):
        return "http://www.mr.is"

class AbsentEmployesAtom(AbsentEmployesRss):
    """
    Prepares Atom feed of absent employees
    """
    feed_type = Atom1Feed
