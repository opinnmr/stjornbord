#coding: utf-8
from django import forms

from stjornbord.student.models import Student
from stjornbord.user.models import INACTIVE_USER

class UsernameForm(forms.Form):
    username    = forms.ChoiceField(widget=forms.RadioSelect, required=True, label="Notandanafn")

class KennitalaForm(forms.Form):
    """
    Form used for looking up students
    """
    kennitala   = forms.CharField()

    def clean_kennitala(self):
        """
        Check that:
         - Kennitala exists
         - Student is active
         - Student has no registered user accounts
        """
        try:
            student = Student.objects.get(kennitala=self.data['kennitala'])
        except Student.DoesNotExist:
            raise forms.ValidationError("Kennitala fannst ekki á skrá")
    
        if not student.status.active:
            raise forms.ValidationError("Nemandi ekki virkur")
    
        if student.userp.exclude(status__id=INACTIVE_USER).count() != 0:
            raise forms.ValidationError("Nemandi þegar skráður með netfang. Minnist þú "+
            "þess ekki að hafa skráð þig fyrir netfangi skalt þú hafa samband við "+
            "kerfisstjóra eða skrifstofu skólans við fyrsta tækifæri.")

        return self.data['kennitala']
