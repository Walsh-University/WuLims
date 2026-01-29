from django import forms
class InstrumentFilterForm(forms.Form):
    # Search query
    q = forms.CharField(required=False, label="Search")

    is_active = forms.ChoiceField(
        required=False,
        choices=[("", "Any"), (True, "Active"), (False, "Inactive")],
        label="Status",
    )

    # Filter by manufacturer
    manufacturer = forms.CharField(required=False, label="Manufacturer")
