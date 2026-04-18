from django import forms
from .models import Subscriber


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email...'
        self.fields['email'].label = False
        self.fields['email'].widget.attrs['class'] = 'border-black rounded-0'