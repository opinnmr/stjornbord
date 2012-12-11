# coding: utf8
import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from stjornbord import settings
from stjornbord.utils import mrnet_only
from stjornbord.student.models import Student
from stjornbord.user.forms import PasswordForm
from stjornbord.user.models import UserProfile, UserStatus, INACTIVE_USER
from stjornbord.register.registration import suggest_usernames
from stjornbord.register.forms import UsernameForm, KennitalaForm

log = logging.getLogger("stjornbord")

@mrnet_only
def register(request):
    context = {}
    
    if request.method == 'POST':
        kennitala_form = KennitalaForm(request.POST)
        if kennitala_form.is_valid():
            student = Student.objects.get(kennitala=kennitala_form.cleaned_data['kennitala'])
            suggested_usernames = suggest_usernames(student.first_name, student.last_name, student.kennitala)

            # See if the user actually posted some stuff, other that its
            # kennitala to get to this page
            post_keys        = request.POST.keys()
            other_post_stuff = None
            if "id_username_0" in post_keys or "password" in post_keys:
                other_post_stuff = request.POST

            password_form = PasswordForm(other_post_stuff)
            username_form = UsernameForm(other_post_stuff)
            username_form.fields['username'].choices = [(x, x) for x in suggested_usernames]

            if username_form.is_valid() and password_form.is_valid():
                username = username_form.cleaned_data['username']
                log.info("Creating user %s for student %s (kt %s)", username,
                    student, student.kennitala)

                user = User.objects.create(username=username, password="sha1$$tmp") # pw overridde below
                userp = UserProfile(
                            user      = user,
                            kennitala = student.kennitala,
                            user_type = ContentType.objects.get_for_model(student),
                            status = UserStatus.objects.get(pk=1),
                        )

                userp.set_password(password_form.cleaned_data['password'])
                userp.set_dirty()
                userp.save()
                
                return HttpResponseRedirect("/register/done/")
                
                
            context['password_form']  = password_form.as_ul()
            context['username_form']  = username_form.as_ul()
            context['student']  = student
    else:
        kennitala_form = KennitalaForm()


    context['kennitala_form'] = kennitala_form.as_ul()

    return render_to_response(
        'registration/register.html', context,
        context_instance=RequestContext(request))
