from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Future-proof fields for AD/SSO
    external_id = models.CharField(max_length=255, blank=True, default="", help_text="SSO subject / GUID")
    employee_id = models.CharField(max_length=64, blank=True, default="")
    department = models.CharField(max_length=128, blank=True, default="")
    customer_profile = models.ForeignKey(
        "customers.Customer",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="portal_users",
    )
    contact_profile = models.OneToOneField(
        "customers.Person",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="portal_user",
    )

    def display_name(self) -> str:
        full: str = self.get_full_name().strip()
        return full if full else (self.email or self.username)  # ty: ignore[invalid-return-type]

    class Meta:
        permissions = [
            ("manage_roles", "Can manage user role assignments"),
        ]


class RoleAssignmentAudit(models.Model):
    class Action(models.TextChoices):
        ASSIGNED = "assigned", "Assigned"
        REMOVED = "removed", "Removed"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="role_assignment_audits",
        help_text="User whose role assignment changed.",
    )
    role_name = models.CharField(max_length=150)
    action = models.CharField(max_length=16, choices=Action.choices)
    changed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="role_assignment_changes_made",
        help_text="Actor that changed the role assignment.",
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-changed_at",)

    def __str__(self) -> str:
        return f"{self.user} {self.action} {self.role_name}"
