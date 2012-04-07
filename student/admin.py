from stjornbord.student.models import Klass, Student
from stjornbord.user.admin import UserInline
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class StudentOptions(admin.ModelAdmin):
    list_display = ('kennitala', 'first_name', 'last_name', 'klass', 'status')
    list_display_links = list_display[:3]
    list_filter  = ('status', 'klass')
    search_fieldsets = ('kennitala', 'first_name', 'last_name')
    
    inlines = [
        UserInline,
    ]
    

admin.site.register(Klass)
admin.site.register(Student, StudentOptions)

