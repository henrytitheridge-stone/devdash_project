from django import forms
from .models import Service


class ServiceForm(forms.ModelForm):
    """
    Administrative services form for frontend CRUD.
    """
    class Meta:
        model = Service
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
