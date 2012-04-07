from stjornbord.user.models import UserStatus, ReserverdUsername, UserProfile, MailingList, PosixUidPool, PosixGroup
from stjornbord.user.forms import ValidateUsernameForm
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic


class UserInline(generic.GenericTabularInline):
    model       = UserProfile
    ct_field    = "user_type"
    ct_fk_field = "kennitala"

class UserProfileOptions(admin.ModelAdmin):
    list_display = ('user', 'kennitala', )
    search_fields = ('kennitala', )
    list_filter = ('status', )
    raw_id_fields   = ('user', )

class MailingListOptions(admin.ModelAdmin):
    form = ValidateUsernameForm

class ReserverdUsernameOptions(admin.ModelAdmin):
    form = ValidateUsernameForm

admin.site.register(UserStatus)
admin.site.register(MailingList, MailingListOptions)
admin.site.register(ReserverdUsername, ReserverdUsernameOptions)
admin.site.register(UserProfile, UserProfileOptions)
admin.site.register(PosixUidPool)
admin.site.register(PosixGroup)
