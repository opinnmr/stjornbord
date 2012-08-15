# coding: utf8
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.views.generic.list_detail import object_list
from django import forms

import hashlib, datetime, os.path, random

from stjornbord.settings import INNA_ROOT
from stjornbord.utils import prep_tmp_dir
from stjornbord.student.parser import InnaParser, InnaParserException
from stjornbord.student.models import Student, Klass
from stjornbord.ou.models import Status
from stjornbord.user.models import UserProfile
from stjornbord.user.printquota import get_printquota, set_printquota
from stjornbord.ou.views import _generic_ou_list
from stjornbord.student.forms import UploadForm, UserForm, PrintQuotaForm

@user_passes_test(lambda u: u.is_superuser)
def inna_upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            prep_tmp_dir(INNA_ROOT)
            filename = "inna_%s_%s" % (datetime.datetime.now().strftime("%Y%m%d%H%M%S"), hashlib.md5(str(random.randrange(10000))).hexdigest())
            inna     = file(os.path.join(INNA_ROOT, "%s.csv" % filename), "wb")
            inna.write(form.cleaned_data['inna_file'].read())
            inna.close()
            
            return HttpResponseRedirect('/students/import/%s/' % filename)
    else:
        form = UploadForm()
    return render_to_response('student/inna_upload.html', {'form': form.as_p() }, context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def inna_import(request, filename):
    pretend = True
    
    if request.method == "POST":
        if "commit" in request.POST:
            pretend = False
    
    ip = InnaParser(os.path.join(INNA_ROOT, "%s.csv" % filename), pretend=pretend)
    
    error = None
    try:
        ip.update()
    except InnaParserException, e:
        error = e.message

    if pretend:
        return render_to_response('student/inna_import.html',
            { 'pretend': pretend, 'stats': ip.stats, 'error': error },
            context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/')


@user_passes_test(lambda u: u.is_superuser)
def export(request):
    # This is optimized for everything but speed.
    # Say hello to 1000 sql queries..
    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s.txt' % datetime.datetime.now().strftime("Students.%Y%m%d.%H%M")
    
    students = Student.objects.filter(status=1)
    for student in students:
        users = student.userp.filter(status__active=1)
        if users:
            response.write("\t%s\t\t\t%s@mr.is\t\t\t\t\n" % (student.kennitala, users[0].user.username))

    return response


@user_passes_test(lambda u: u.is_superuser)
def list(request):
    filter_items = {
        'status':   Status.objects.all(),
        'klass':    Klass.objects.all(),
        }
    return _generic_ou_list(request, Student, filter_items, 'student/list.html')


@user_passes_test(lambda u: u.is_superuser)
def edit_user(request, kennitala, user_id):
    """
    This is basically just a stripped down version of the OU's edit_user, as we
    only want to be able to change passwords
    """
    student = get_object_or_404(Student, pk=kennitala)
    userp   = get_object_or_404(UserProfile, pk=user_id, kennitala=kennitala)

    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['password']:
                userp.set_password(form.cleaned_data['password'])
                userp.save()
            return HttpResponseRedirect("/students/list/")
    else:
        form = UserForm()

    return render_to_response('student/edit_user.html', {'form': form.as_ul(), 'userp': userp }, context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def change(request, kennitala):
    student = get_object_or_404(Student, pk=kennitala)
    StudentForm = forms.models.modelform_factory(
                            Student,
                            fields=('status', )
                            )

    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/students/list/")
    else:
        form = StudentForm(instance=student)

    return render_to_response(
        'student/edit.html', {'student': student, 'form': form.as_ul(), },
        context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def printquota(request, kennitala, user_id):
    student = get_object_or_404(Student, pk=kennitala)
    userp   = get_object_or_404(UserProfile, pk=user_id, kennitala=kennitala)
    noquota = False

    if request.method == "POST":
        form = PrintQuotaForm(request.POST)
        if form.is_valid():
            set_printquota(userp.user, form.cleaned_data['balance'])
            return HttpResponseRedirect("/students/list/")
    else:
        balance = get_printquota(userp.user)
        noquota = balance is None
        form = PrintQuotaForm(initial={'balance': balance})

    return render_to_response('student/printquota.html',
        {
            'form':    form.as_ul(),
            'userp':   userp,
            'noquota': noquota,
        },
        context_instance=RequestContext(request))

