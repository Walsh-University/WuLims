from django import forms
from .models import Instrument

class InstrumentFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Search")
    is_active = forms.ChoiceField(
        required=False,
        choices=[("", "Any"), (True, "Active"), (False, "Inactive")],
        label="Status",
    )
    manufacturer = forms.CharField(required=False, label="Manufacturer")
