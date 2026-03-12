from django import forms

from customers.models import Customer


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["customer_name", "external_id", "customer_type"]
        labels = {
            "customer_name": "Company name",
            "external_id": "Customer identifier",
            "customer_type": "Company type",
        }
        widgets = {
            "customer_name": forms.TextInput(attrs={"class": "form-control"}),
            "external_id": forms.TextInput(attrs={"class": "form-control"}),
            "customer_type": forms.TextInput(attrs={"class": "form-control"}),
        }
        error_messages = {
            "external_id": {
                "unique": "A company profile with this customer identifier already exists.",
            }
        }
