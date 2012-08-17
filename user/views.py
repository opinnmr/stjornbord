# coding: utf8
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse
from stjornbord.user.forms import ChangePasswordForm
from stjornbord.user.models import UserProfile
from stjornbord.user.printquota import get_printquota
from stjornbord.utils import mrnet_only, verify_sync_secret
from django.contrib.auth.models import User
import simplejson

def frontpage(request):
    quota   = get_printquota(request.user)
    noquota = quota is None

    c = {
        "quota":    quota,
        "noquota":  noquota,
    }
    
    return direct_to_template(request, 'frontpage.html', extra_context=c)

@login_required
def change_password(request):
    done = False
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        form.set_username_pre_clean(request.user.username)
        if form.is_valid():
            userp = request.user.get_profile()
            userp.set_password(form.cleaned_data["password"])
            userp.save()
            done = True
    else:
        form = ChangePasswordForm()
    
    return render_to_response(
        'user/change_password.html',
        {'form': form.as_ul(), 'done': done },
        context_instance=RequestContext(request))

@csrf_exempt
@mrnet_only
def sync_get_dirty(request):
    dirty = UserProfile.objects.filter(dirty__gt=0)
    response = HttpResponse(mimetype="application/json")

    exp = []
    for up in dirty:
        exp.append({
            'type':         'user',
            'username':     up.user.username,
            'posix_uid':    up.posix_uid,
            'tmppass':      up.tmppass,
            'fullname':     up.content_object.get_fullname(),
            'first_name':   up.content_object.first_name,
            'last_name':    up.content_object.last_name,
            'groups':       [],
            'status':       up.status.pk,
            'dirty':        up.dirty,
        })

    simplejson.dump(exp, response)
    from django.db import connection
    for l in connection.queries:
        print l['sql']
    return response

@csrf_exempt
@mrnet_only
@verify_sync_secret
def sync_clean_dirty(request, username, timestamp):
    user = get_object_or_404(User, username=username)
    response = HttpResponse("ok", mimetype="text/plain")
    user.clear_dirty(timestamp)
    return response