from django import forms
from .models import Sample

class SampleFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Search")
    status = forms.ChoiceField(
        required=False,
        choices=[("", "Any")] + list(Sample.Status.choices),
        label="Status",
    )
