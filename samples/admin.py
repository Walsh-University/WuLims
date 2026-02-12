from django.contrib import admin

from .models import Sample


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ("sample_id", "project", "client_name", "status", "received_at", "approved_at")
    search_fields = ("sample_id", "project__name", "client_name")
    list_filter = ("project", "status")
