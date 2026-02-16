from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db import models

from audit.models import AuditEvent


def log_audit_event(*, user=None, action: str, instance: models.Model, diff: dict[str, Any] | None = None) -> None:
    AuditEvent.objects.create(
        actor=user,
        action=action,
        object_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        changes=diff,
    )
