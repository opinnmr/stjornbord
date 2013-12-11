from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import stjornbord.register.views
import stjornbord.student.views
import stjornbord.user.views
import stjornbord.ou.views
import stjornbord.devices.views
import stjornbord.infoscreen.views
import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$',       stjornbord.user.views.frontpage),

    (r'^register/$', stjornbord.register.views.register),
    (r'^register/done/$', direct_to_template, {'template': 'registration/done.html'}),
    

    (r'^login/$',           'django.contrib.auth.views.login'),
    (r'^logout/$',          'django.contrib.auth.views.logout', {'next_page': '/logged_out/'}),
    (r'^logged_out/$',      direct_to_template, {'template': 'logged_out.html'}),
    (r'^change_password/$', stjornbord.user.views.change_password),

    (r'^students/upload/$',                         stjornbord.student.views.inna_upload),
    (r'^students/import/(?P<filename>[\w_]+)/$',    stjornbord.student.views.inna_import),
    (r'^students/list/$',                           stjornbord.student.views.list),
    (r'^students/export/$',                         stjornbord.student.views.export),
    (r'^students/(?P<kennitala>\d{10})/$',                  stjornbord.student.views.change),
    (r'^students/(?P<kennitala>\d{10})/(?P<user_id>\d+)/$', stjornbord.student.views.edit_user),
    (r'^students/(?P<kennitala>\d{10})/(?P<user_id>\d+)/printquota/$', stjornbord.student.views.printquota),

    (r'^ou/add/$',                                      stjornbord.ou.views.add),
    (r'^ou/list/$',                                     stjornbord.ou.views.list),
    (r'^ou/(?P<kennitala>\d{10})/$',                    stjornbord.ou.views.change),
    (r'^ou/(?P<kennitala>\d{10})/add_user/$',           stjornbord.ou.views.edit_user, {'user_id': None}),
    (r'^ou/(?P<kennitala>\d{10})/(?P<user_id>\d+)/$',   stjornbord.ou.views.edit_user),
    
    (r'^ou/(?P<kennitala>\d{10})/add_list/$',           stjornbord.ou.views.edit_mailinglist, {'list_id': None}),
    (r'^ou/(?P<kennitala>\d{10})/mailinglist/(?P<list_id>\d+)/$',   stjornbord.ou.views.edit_mailinglist),

    # User and device synchronization
    (r'^devices/export/$',                  stjornbord.devices.views.export),
    (r'^counter/(?P<name>[\w]+)/$',         stjornbord.devices.views.counter),
    (r'^dirty/users/$',                     stjornbord.user.views.sync_get_dirty),
    (r'^clean/user/(?P<username>\w+)/(?P<timestamp>\d+)/$', stjornbord.user.views.sync_clean_dirty),

    # Infoscreen
    (r'^infoscreen/json/$',     stjornbord.infoscreen.views.json),
    (r'^infoscreen/screen/$',   stjornbord.infoscreen.views.screen),
    (r'^infoscreen/rss/$',      stjornbord.infoscreen.views.AbsentEmployesRss()),
    (r'^infoscreen/atom/$',     stjornbord.infoscreen.views.AbsentEmployesAtom()),

    # This should one day either be moved to flatpages or made somehow more dynamic
    (r'^help/$',                 direct_to_template, {'template': 'help/index.html'}),
    (r'^help/change_password/$', direct_to_template, {'template': 'help/change_password.html'}),
    (r'^help/lost_password/$',   direct_to_template, {'template': 'help/lost_password.html'}),
    (r'^help/export_mail/$',     direct_to_template, {'template': 'help/export_mail.html'}),
    (r'^help/printquota/$',     direct_to_template, {'template': 'help/printquota.html'}),

    (r'^admin/', include(admin.site.urls)),
)

# Only load the SSO module if enabled. This pulls in saml2 and xmlsec dependencies.
if settings.GOOGLE_SSO_ENABLE:
    import stjornbord.saml2idp.views
    sso_action = (r'^sso/$', stjornbord.saml2idp.views.assertView)
else:
    sso_action = (r'^sso/$', direct_to_template, {'template': 'registration/sso_disabled.html'})
urlpatterns += patterns('', sso_action)

# Serve static content during development
urlpatterns += staticfiles_urlpatterns()