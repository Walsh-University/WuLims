from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import RoleAssignmentAudit, User
from .roles import resolve_manage_roles_permission_codename


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("University/SSO", {"fields": ("external_id", "employee_id", "department")}),)
    list_display = ("username", "email", "first_name", "last_name", "department", "is_staff")

    def _can_manage_roles(self, request):
        return request.user.is_superuser or request.user.has_perm(resolve_manage_roles_permission_codename())

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if not self._can_manage_roles(request):
            readonly.append("groups")
        if not request.user.is_superuser:
            readonly.extend(["is_superuser", "user_permissions"])
        return tuple(readonly)


try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


@admin.register(Group)
class RoleGroupAdmin(DjangoGroupAdmin):
    def _can_manage_roles(self, request):
        return request.user.is_superuser or request.user.has_perm(resolve_manage_roles_permission_codename())

    def has_module_permission(self, request):
        return self._can_manage_roles(request)

    def has_view_permission(self, request, obj=None):
        return self._can_manage_roles(request)

    def has_add_permission(self, request):
        return self._can_manage_roles(request)

    def has_change_permission(self, request, obj=None):
        return self._can_manage_roles(request)

    def has_delete_permission(self, request, obj=None):
        return self._can_manage_roles(request)


@admin.register(RoleAssignmentAudit)
class RoleAssignmentAuditAdmin(admin.ModelAdmin):
    list_display = ("changed_at", "user", "role_name", "action", "changed_by")
    list_filter = ("action", "role_name")
    search_fields = ("user__username", "user__email", "changed_by__username", "changed_by__email", "role_name")
    ordering = ("-changed_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
