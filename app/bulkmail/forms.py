from django import forms


class BulkmailForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100)
    text = forms.CharField(label="Text", max_length=1500)
    media = forms.URLField()

