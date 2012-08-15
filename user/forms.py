# coding: utf8
from django import forms
from django.contrib.auth import authenticate

from stjornbord.user.models import UserStatus, validate_username

class ValidateUsernameForm(forms.ModelForm):
    """
    Used in Django's admin to verify Kennitala and usernames
    """
    def clean_kennitala(self):
        kennitala = self.data['kennitala']
        if not (len(kennitala) == 10 and kennitala.isdigit()):
            raise forms.ValidationError("Kennitala skal vera samsett af 10 tölustöfum")
            
        return kennitala
    
    # This could be done as clean_username but then we can't depend on the
    # other fields having been cleaned.
    def clean(self):
        clean_username(self)
        return forms.ModelForm.clean(self)

def clean_username(form_object, current_holder=None):
    # Only verify username if other fields passed their verification
    if not form_object.errors:
        status_id = None
        kennitala = None

        if "status" in form_object.cleaned_data:
            status_id = form_object.cleaned_data['status']

            # If we are running this from the admin, the cleaned value is the
            # model instance itself, not only the id.
            if type(status_id) is UserStatus:
                status_id = status_id.id

        if "kennitala" in form_object.cleaned_data:
            kennitala = form_object.cleaned_data['kennitala']

        validate_username(
                    form_object.cleaned_data['username'],
                    current_holder=current_holder
                    )

PASSWORD_MIN_LENGTH = 8

def _clean_password(self):
    """
    Verify that passwords match
    """
    if self.data['password'] != self.data['password2']:
        raise forms.ValidationError("Lykilorð stemma ekki")
    
    password = self.data['password']
    if len(password) < PASSWORD_MIN_LENGTH:
        raise forms.ValidationError("Lykilorðið þarf að vera minnst %d stafir" % PASSWORD_MIN_LENGTH)

    # Copied from http://stackoverflow.com/questions/5226329/enforcing-password-strength-requirements-with-django-contrib-auth-views-password
    first_isalpha = password[0].isalpha()
    if all(c.isalpha() == first_isalpha for c in password):
        raise forms.ValidationError("Lykilorðið þarf að innihalda amk einn bókstaf og "
                    "einn tölustaf eða greinarmerki.")
    
    return self.data['password']

# Note: This form is also used when new students are registering for
# accounts. Handle with care!
class PasswordForm(forms.Form):
    password        = forms.CharField(widget=forms.PasswordInput(), label="Lykilorð")
    password2       = forms.CharField(widget=forms.PasswordInput(), label="Lykilorð, aftur")
    
    clean_password = _clean_password

class ChangePasswordForm(forms.Form):
    current         = forms.CharField(widget=forms.PasswordInput(), label="Núverandi lykilorð")
    password        = forms.CharField(widget=forms.PasswordInput(), label="Nýtt lykilorð")
    password2       = forms.CharField(widget=forms.PasswordInput(), label="Nýtt lykilorð, aftur")

    clean_password  = _clean_password

    def set_username_pre_clean(self, username):
        """
        Used to pass the current user's username to the form
        for current password validation.
        """
        self._username = username

    def clean_current(self):
        user = authenticate(username=self._username, password=self.data['current'])

        if user is None:
            raise forms.ValidationError("Núverandi lykilorð er rangt.")
        return self.data['current']

