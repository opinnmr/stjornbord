from stjornbord.ou.models import Status, Group, OrganizationalUnit
from stjornbord.user.admin import UserInline
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class OrganizationalUnitOptions(admin.ModelAdmin):
    list_display = ('kennitala', 'first_name', 'last_name', 'group')
    list_display_links = list_display[:3]
    list_filter  = ('group', )
    search_fields = ('kennitala', 'first_name', 'last_name')

    inlines = [
        UserInline,
    ]

admin.site.register(Status)
admin.site.register(Group)
admin.site.register(OrganizationalUnit, OrganizationalUnitOptions)

