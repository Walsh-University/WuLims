from django import forms


class ExperimentFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Search")

    is_active = forms.ChoiceField(
        required=False,
        choices=[("", "Any"), (True, "Active"), (False, "Inactive")],
        label="Status",
    )

    project = forms.CharField(required=False, label="Project")
