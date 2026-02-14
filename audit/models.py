from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

User = get_user_model()


class AuditEvent(models.Model):
    actor = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    action = models.CharField(
        max_length=50,
    )

    object_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("object_type", "object_id")

    before = models.JSONField(
        null=True,
        blank=True,
    )
    after = models.JSONField(
        null=True,
        blank=True,
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
    )

    meta = models.JSONField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.action} on {self.object_type} ({self.object_id})"
