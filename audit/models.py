from django.conf import settings
from django.db import models


class AuditEvent(models.Model):
    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("status_change", "Status change"),
        ("system", "System action"),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_events",
        help_text="User who performed the action. Null means system action.",
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the action occurred.",
    )

    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        help_text="Type of action performed.",
    )

    object_type = models.CharField(
        max_length=100,
        help_text="Model name of the affected object (e.g. Experiment, Sample).",
    )

    object_id = models.UUIDField(
        help_text="Primary key of the affected object.",
    )

    diff = models.JSONField(
        null=True,
        blank=True,
        help_text="Field-level changes: {field: {from: x, to: y}}",
    )

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["object_type", "object_id"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self) -> str:
        actor = self.actor if self.actor else "system"
        return f"[{self.timestamp}] {actor} {self.action} {self.object_type}({self.object_id})"
