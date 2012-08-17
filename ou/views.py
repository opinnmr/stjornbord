# coding: utf-8
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic.list_detail import object_list
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.forms.models import modelform_factory

from stjornbord.ou.models import OrganizationalUnit, Status, Group
from stjornbord.user.models import UserProfile, UserStatus, MailingList
from stjornbord.ou.forms import UserForm, MailingListForm, SearchForm, OrganizationalUnitBase

from stjornbord.google.api import Google

def _generic_ou_list(request, model, filter_items, template_name):
    """
    Helper function to list `model` objects, filtered by `filter_items`.
    Fetches results and invokes Django's generic view object list.
    """
    qs = model.objects.all()
    filters = {}
    
    for f in filter_items.keys():
        value   = request.GET.get(f, None)
        if value:
            try:
                filters[f] = int(value)
            except:
                pass

    qs = qs.filter(**filters)
    
    search_form = SearchForm(request.POST)
    search_form.is_valid() # generate cleaned_data
    search_query = search_form.cleaned_data["query"]
    if search_query:
        qs &= (
                qs.filter(first_name__icontains=search_query)
                | qs.filter(last_name__icontains=search_query)
                | qs.filter(kennitala__startswith=search_query)
                )
    
    context  = {
        "filters": filters,
        "filter_items": filter_items,
        "search_form": search_form,
        }
    
    return object_list(request, qs, template_name=template_name,
        paginate_by=100, extra_context=context)


@user_passes_test(lambda u: u.is_superuser)
def add(request):
    return _edit_ou(request)


@user_passes_test(lambda u: u.is_superuser)
def change(request, kennitala):
    ou = get_object_or_404(OrganizationalUnit, pk=kennitala)
    return _edit_ou(request, ou)


def _edit_ou(request, ou=None):
    """
    Edit this Organizational unit
    """
    if ou:
        title = u"Breyta starfsmanni"
    else:
        title = u"Bæta við starfsmanni"

    form_klass = modelform_factory(
        OrganizationalUnit,
        form=OrganizationalUnitBase,
        exclude=('kennitala', ) if ou else None,
    )

    if request.method == "POST":
        form = form_klass(request.POST, instance=ou)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/ou/list/")
    else:
        form = form_klass(instance=ou)

    return render_to_response(
        'ou/edit.html',
        {'form': form.as_ul(), 'title': title },
        context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def list(request):
    filter_items = {
        'status':   Status.objects.all(),
        'group':    Group.objects.all(),
        }
    
    return _generic_ou_list(request, OrganizationalUnit, filter_items, 'ou/list.html')


@user_passes_test(lambda u: u.is_superuser)
def edit_user(request, kennitala, user_id=None):
    ou   = get_object_or_404(OrganizationalUnit, pk=kennitala)

    if user_id:
        userp  = get_object_or_404(UserProfile, pk=user_id, kennitala=kennitala)
        title = u"Breyta notanda"
    else:
        userp  = None
        title = u"Bæta við notanda"

    if request.method == "POST":
        user = None
        form = UserForm(request.POST)
        if form.is_valid(current_holder=userp):
            if not user_id:
                user = User.objects.create(username=form.cleaned_data['username'], password="sha1$$tmp")
                userp = UserProfile(
                            user      = user,
                            kennitala = ou.kennitala,
                            user_type = ContentType.objects.get_for_model(ou),
                        )

            userp.status = UserStatus.objects.get(pk=form.cleaned_data['status'])
            
            if form.cleaned_data['password']:
                userp.set_password(form.cleaned_data['password'])

            userp.set_dirty()
            userp.save()

            return HttpResponseRedirect("/ou/list/")
    else:
        initial = {'kennitala': kennitala, 'status': 1}
        
        if user_id:
            initial['status']     = userp.status.id
            initial['username']   = userp.user.username
        
        form = UserForm(initial=initial)

    return render_to_response('ou/edit.html',
        {'form': form.as_ul(), 'title': title, 'userp': userp,
            'editwarning': True if userp else False },
        context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def edit_mailinglist(request, kennitala, list_id=None):
    ou   = get_object_or_404(OrganizationalUnit, pk=kennitala)

    if list_id:
        mailinglist = get_object_or_404(MailingList, pk=list_id, kennitala=kennitala)
        title       = u"Breyta póstlista"
    else:
        mailinglist = None
        title       = u"Bæta við póstlista"

    if request.method == "POST":
        form = MailingListForm(request.POST)
        if form.is_valid(current_holder=mailinglist):
            if not list_id:
                mailinglist = MailingList(
                            username=form.cleaned_data['username'],
                            kennitala = ou.kennitala,
                            user_type = ContentType.objects.get_for_model(ou),
                        )
                mailinglist.save()
            
            members = [addr.strip() for addr in form.cleaned_data['members'].split('\n') if "@" in addr]
            Google().list_sync(mailinglist.username, members)
            
            return HttpResponseRedirect("/ou/list/")
    else:
        initial = {'kennitala': kennitala}

        if list_id:
            initial['username'] = mailinglist.username
            initial['members']  = "\n".join(Google().list_members(mailinglist.username))

        form = MailingListForm(initial=initial)

    return render_to_response('ou/edit.html', {'form': form.as_ul(), 'title': title }, context_instance=RequestContext(request))
