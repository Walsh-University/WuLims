from django import forms

from .models import Sample


class SampleFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Search")
    status = forms.ChoiceField(
        required=False,
        choices=[("", "Any")] + list(Sample.Status.choices),
        label="Status",
    )


class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ["client_name", "status", "approved_at", "approved_by"]
        widgets = {
            "client_name": forms.TextInput(attrs={"class": "form-control"}),
        }
