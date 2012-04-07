from stjornbord.devices.models import *
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class PrefixAdmin(admin.ModelAdmin):
    list_display = ('name', 'dns')

class SubdomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'dns')

class VlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'network')

admin.site.register(Subdomain, SubdomainAdmin)
admin.site.register(Prefix, PrefixAdmin)
admin.site.register(Vlan, VlanAdmin)
admin.site.register(Device)
admin.site.register(Counter)

