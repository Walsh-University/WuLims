from django import forms

from .models import Customer


class CustomerFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Search")

    is_active = forms.TypedChoiceField(
        required=False,
        label="is_active",
        choices=[("", "Any")] + list(Customer._meta.get_field("is_active").choices),
        coerce=lambda v: {"True": True, "False": False}.get(v, v),
        empty_value="",
    )


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["customer_name", "is_active",]
        widgets = {
            "customer_name": forms.TextInput(attrs={"class": "form-control"}),
        }