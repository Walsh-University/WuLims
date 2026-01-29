from django.contrib import admin
from .models import Instrument


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    # какие поля показываются в списке
    list_display = (
        "name",
        "manufacturer",
        "model",
        "serial_number",
        "is_active",
        "last_calibration_date",
        "last_maintenance_date",
    )

    # поиск по этим полям
    search_fields = ("name", "manufacturer", "model", "serial_number")

    # фильтр в боковой панели
    list_filter = ("is_active", "manufacturer")

    # сортировка по умолчанию
    ordering = ("name",)
