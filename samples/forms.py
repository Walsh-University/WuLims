from django import forms
from django.db.models import Q

from .models import AnalysisType, Sample, SampleAnalysis


class SampleFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Search")
    status = forms.ChoiceField(
        required=False,
        choices=[("", "Any")] + list(Sample.Status.choices),
        label="Status",
    )


class SampleForm(forms.ModelForm):
    analysis_types = forms.ModelMultipleChoiceField(
        queryset=AnalysisType.objects.none(),
        required=False,
        label="Analysis Types",
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": "6"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assigned_ids = []
        if self.instance and self.instance.pk:
            assigned_ids = list(self.instance.analyses.values_list("analysis_type_id", flat=True))

        self.fields["analysis_types"].queryset = AnalysisType.objects.filter(
            Q(is_active=True) | Q(pk__in=assigned_ids)
        ).order_by("sort_order", "name")
        self.initial["analysis_types"] = assigned_ids

    def save(self, commit=True):
        sample = super().save(commit=commit)
        if not commit:
            return sample

        selected = self.cleaned_data.get("analysis_types", [])
        selected_ids = {analysis_type.pk for analysis_type in selected}
        existing_qs = SampleAnalysis.objects.filter(sample=sample)
        existing_ids = set(existing_qs.values_list("analysis_type_id", flat=True))

        to_remove = existing_ids - selected_ids
        to_add = selected_ids - existing_ids

        if to_remove:
            existing_qs.filter(analysis_type_id__in=to_remove).delete()
        if to_add:
            SampleAnalysis.objects.bulk_create(
                [SampleAnalysis(sample=sample, analysis_type_id=analysis_type_id) for analysis_type_id in to_add]
            )

        return sample

    class Meta:
        model = Sample
        fields = ["sample_name", "project", "client_name", "status", "approved_at", "approved_by"]
        widgets = {
            "sample_name": forms.TextInput(attrs={"class": "form-control"}),
            "project": forms.Select(attrs={"class": "form-select"}),
            "client_name": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "approved_by": forms.Select(attrs={"class": "form-select"}),
        }
