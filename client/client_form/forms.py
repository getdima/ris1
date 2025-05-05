from django import forms
 
class RequestForm(forms.Form):
    hash = forms.CharField()
    maxLength = forms.IntegerField(min_value=1)

class RequestStatusForm(forms.Form):
    request = forms.CharField()

class WorkerProgressForm(forms.Form):
    worker = forms.IntegerField(min_value=0)