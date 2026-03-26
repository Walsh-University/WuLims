from django import forms

from projects.models import Project, ProjectRequest


class ProjectFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Search")
    status = forms.ChoiceField(
        required=False,
        choices=[("", "Any")] + list(Project.Status.choices),
        label="Status",
    )


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "status",
            "start_date",
            "completed_date",
            "customer_id",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "completed_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "customer_id": forms.Select(attrs={"class": "form-select"}),
        }


class ProjectRequestForm(forms.ModelForm):
    class Meta:
        model = ProjectRequest
        fields = [
            "title",
            "description",
            "business_context",
            "scientific_context",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "business_context": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "scientific_context": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
