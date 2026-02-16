from django.contrib import admin

from .models import AnalysisType, Sample, SampleAnalysis


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ("sample_id", "project", "client_name", "status", "received_at", "approved_at")
    search_fields = ("sample_id", "project__name", "client_name")
    list_filter = ("project", "status")


@admin.register(AnalysisType)
class AnalysisTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "sort_order")
    search_fields = ("code", "name")
    list_filter = ("is_active",)
    ordering = ("sort_order", "name")


@admin.register(SampleAnalysis)
class SampleAnalysisAdmin(admin.ModelAdmin):
    list_display = ("sample", "analysis_type", "requested_at")
    search_fields = ("sample__sample_id", "sample__sample_name", "analysis_type__code", "analysis_type__name")
    list_filter = ("analysis_type", "requested_at")
