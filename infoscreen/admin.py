from stjornbord.infoscreen.models import *
from django.contrib import admin

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'visible')
    list_filter  = ('visible', )

class EmployeesInline(admin.TabularInline):
    model       = AbsentRelation

class AbsentEmployeesAdmin(admin.ModelAdmin):
    list_display = ('date', )

    inlines = [
        EmployeesInline,
    ]

admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(AbsentEmployees, AbsentEmployeesAdmin)
