import csv
import json

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html

from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "actor",
        "action",
        "object_type",
        "object_id",
    )

    list_filter = (
        "actor",
        "action",
        "object_type",
        "timestamp",
    )

    search_fields = ("object_id",)
    ordering = ("-timestamp",)

    readonly_fields = (
        "timestamp",
        "actor",
        "action",
        "object_type",
        "object_id",
        "formatted_changes",
    )

    fields = (
        "timestamp",
        "actor",
        "action",
        "object_type",
        "object_id",
        "formatted_changes",
    )

    actions = ["export_as_csv"]

    # --- Форматированный вывод before/after ---
    def formatted_changes(self, obj):
        if not obj.changes:
            return "-"
        return format_html("<pre>{}</pre>", json.dumps(obj.changes, indent=2))

    formatted_changes.short_description = "Changes"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=audit_logs.csv"

        writer = csv.writer(response)
        writer.writerow(
            [
                "timestamp",
                "actor",
                "action",
                "object_type",
                "object_id",
                "changes",
            ]
        )

        for obj in queryset:
            writer.writerow(
                [
                    obj.timestamp,
                    obj.actor,
                    obj.action,
                    obj.object_type,
                    obj.object_id,
                    json.dumps(obj.changes),
                ]
            )

        return response

    export_as_csv.short_description = "Export selected to CSV"
