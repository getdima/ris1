from django import forms
 
class RequestForm(forms.Form):
    hash = forms.CharField(required=False)
    maxLength = forms.IntegerField(min_value=1, required=False)

class RequestStatusForm(forms.Form):
    request = forms.CharField(required=False)