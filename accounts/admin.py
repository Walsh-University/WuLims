from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("University/SSO", {"fields": ("external_id", "employee_id", "department")}),)
    list_display = ("username", "email", "first_name", "last_name", "department", "is_staff")
