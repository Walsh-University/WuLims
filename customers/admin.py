from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class SampleAdmin(admin.ModelAdmin):
    list_display = ("customer_id", "customer_name", "external_id", "customer_type", "created_at", "is_active")
    search_fields = ("customer_id", "customer_name")
    list_filter = ("is_active",)