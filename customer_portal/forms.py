from django import forms

from customer_portal.models import ProjectRequest
from customers.models import Customer, Person


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


class ContactProfileForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ["title", "first_name", "last_name", "job_title", "is_active"]
        labels = {
            "is_active": "Active contact",
        }
        widgets = {
            "title": forms.Select(attrs={"class": "form-select"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "job_title": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ProjectRequestForm(forms.ModelForm):
    class Meta:
        model = ProjectRequest
        fields = ["business_context", "scientific_context"]
        labels = {
            "business_context": "Business Context & Objectives",
            "scientific_context": "Scientific Background & Methodology",
        }
        widgets = {
            "business_context": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Describe the business objectives, project scope, and any constraints...",
                }
            ),
            "scientific_context": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Provide scientific background, methodology, and any special requirements...",
                }
            ),
        }
