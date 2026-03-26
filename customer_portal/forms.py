from django import forms

from customers.models import Customer

from .models import CustomerContact


class CustomerContactForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))

    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = CustomerContact
        fields = ["title", "job_title", "active"]

        widgets = {
            "title": forms.Select(attrs={"class": "form-control"}),
            "job_title": forms.TextInput(attrs={"class": "form-control"}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        self.fields["first_name"].initial = user.first_name
        self.fields["last_name"].initial = user.last_name

        self.user = user

    def save(self, commit=True):
        contact = super().save(commit=False)

        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]

        if commit:
            self.user.save()
            contact.save()

        return contact


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
