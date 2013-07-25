from django import forms

class DocumentForm(forms.Form):
    docfile = forms.FileField( label='Select a file', )
    password = forms.CharField(widget=forms.PasswordInput)
