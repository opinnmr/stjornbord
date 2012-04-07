# coding: utf-8
from django import forms

class UploadForm(forms.Form):
    """
    Form used uploading inna file to server
    """
    inna_file   = forms.FileField()

class UserForm(forms.Form):
    """
    Used to change a student's password
    """
    password        = forms.CharField(label=u"Lykilorð", required=True)

class PrintQuotaForm(forms.Form):
    """
    Used to change a student's print quota balance
    """
    balance = forms.IntegerField(label=u"Blaðsíður", required=True)