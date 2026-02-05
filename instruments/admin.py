from django.contrib import admin

from .models import Instrument


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "manufacturer",
        "model",
        "serial_number",
        "is_active",
        "last_calibration_date",
        "last_maintenance_date",
    )

    search_fields = ("name", "manufacturer", "model", "serial_number")
    list_filter = ("is_active", "manufacturer")
    ordering = ("name",)
