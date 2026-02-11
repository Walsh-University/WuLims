from django import forms

from .models import Result


class ResultsFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Search")
    status = forms.ChoiceField(
        required=False,
        choices=[("", "Any")] + list(Result.Status.choices),
        label="Status",
    )


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ["project", "sample", "title", "description", "status"]
        widgets = {
            "project": forms.Select(attrs={"class": "form-select"}),
            "sample": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
