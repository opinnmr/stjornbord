# coding: utf-8
from django import forms

from stjornbord.ou.models import OrganizationalUnit, Status, Group
from stjornbord.user.models import UserProfile, UserStatus, MailingList
from stjornbord.user.forms import clean_username

class UserForm(forms.Form):
    username        = forms.CharField(help_text=u"Ekki með @mr.is", label=u"Notandanafn")
    password        = forms.CharField(widget=forms.PasswordInput(), label=u"Lykilorð", required=False)
    status          = forms.ChoiceField(choices=[(s.id, s.name) for s in UserStatus.objects.all()], label=u"Staða")
    kennitala       = forms.CharField(widget=forms.HiddenInput()) # Used for username validation

    def is_valid(self, *args, **kwargs):
        self._current_holder = kwargs.pop("current_holder", None)
        return forms.Form.is_valid(self)

    def clean(self):
        current_holder = getattr(self, "_current_holder", None)
        clean_username(self, current_holder)
        return forms.Form.clean(self)


class MailingListForm(forms.Form):
    username        = forms.CharField(help_text=u"Ekki með @mr.is", label=u"Netfang")
    kennitala       = forms.CharField(widget=forms.HiddenInput()) # Used for username validation
    members         = forms.CharField(widget=forms.Textarea(), label=u"Áskrifendur", help_text=u"Eitt netfang í hverja línu, passa að öll netföng séu lögleg!")

    def is_valid(self, *args, **kwargs):
        self._current_holder = kwargs.pop("current_holder", None)
        return forms.Form.is_valid(self)

    def clean(self):
        current_holder = getattr(self, "_current_holder", None)
        clean_username(self, current_holder)
        return forms.Form.clean(self)


class SearchForm(forms.Form):
    query   = forms.CharField(label=u"Leitarskilyrði", required=False)

class OrganizationalUnitBase(forms.ModelForm):
    def clean_kennitala(self):
        """
        Verify that kennitala looks right
        """
    def clean_kennitala(self):
        kennitala = self.data['kennitala']
        if not (len(kennitala) == 10 and kennitala.isdigit()):
            raise forms.ValidationError("Kennitala skal vera samsett af 10 tölustöfum")

        return kennitala
        
    class Meta:
        model = OrganizationalUnit