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
        fields = ["project", "client_name", "status", "approved_at", "approved_by"]
        widgets = {
            "project": forms.Select(attrs={"class": "form-select"}),
            "client_name": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "approved_by": forms.Select(attrs={"class": "form-select"}),
        }
