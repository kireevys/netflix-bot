from bulkmail.models import Message
from django import forms


class BulkmailForm(forms.Form):
    text = forms.CharField(max_length=1024, required=True)
    content = forms.URLField(required=False)

    class Meta:
        model = Message
