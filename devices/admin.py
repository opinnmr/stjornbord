from stjornbord.devices.models import *
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class PrefixAdmin(admin.ModelAdmin):
    list_display = ('name', 'dns')

class SubdomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'dns')

class VlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'network')

class DeviceAdmin(admin.ModelAdmin):
    list_filter  = ('subdomain', 'prefix', 'vlan', )
    search_fields = ('name',)

admin.site.register(Subdomain, SubdomainAdmin)
admin.site.register(Prefix, PrefixAdmin)
admin.site.register(Vlan, VlanAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Counter)

