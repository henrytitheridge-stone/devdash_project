from django import forms
from .models import Subscriber, Enquiry


class SubscriberForm(forms.ModelForm):
    """
    Form for the newsletter subscription.
    Captures user email addresses to be stored in the Subscriber model.
    """
    class Meta:
        model = Subscriber
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email...'
        self.fields['email'].label = False
        self.fields['email'].widget.attrs['class'] = 'border-black rounded-0'


class EnquiryForm(forms.ModelForm):
    """
    Form for the contact page.
    Allows users to send messages which are saved as Enquiry instances
    for administrative follow-up.
    """
    class Meta:
        model = Enquiry
        fields = ('name', 'email', 'subject', 'message')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
