from django.contrib import admin

from projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "status",
        "turnaround_time",
        "start_date",
        "completed_date",
        "customer_id",
    )

    list_filter = (
        "status",
        "turnaround_time",
        "start_date",
    )

    search_fields = (
        "name",
        "description",
    )