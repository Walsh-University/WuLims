from django import forms

from projects.models import Project


class ProjectFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Search")
    status = forms.ChoiceField(
        required=False,
        choices=[("", "Any")] + list(Project.Status.choices),
        label="Status",
    )
