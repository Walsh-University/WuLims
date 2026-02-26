from django import forms

from .models import Customer


class CustomerFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Search")

    is_active = forms.ChoiceField(
        required=False,
        label="Status",
        choices=[("", "Any")] + list(Customer._meta.get_field("is_active").choices),
    )


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "customer_name",
            "external_id",
            "customer_type",
            "is_active",
        ]
        widgets = {
            "customer_name": forms.TextInput(attrs={"class": "form-control"}),
            "external_id": forms.TextInput(attrs={"class": "form-control"}),
            "customer_type": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.Select(attrs={"class": "form-select"}),
        }
