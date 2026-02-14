from typing import Any

from django.db import models
from django.contrib.contenttypes.models import ContentType

from audit.models import AuditEvent


def log_audit_event(
    *,
    user,
    action: str,
    instance: models.Model,
    diff: dict[str, Any] | None = None,
) -> None:
    """
    Create an audit event for a domain object.

    user: User instance or None (None = system action)
    action: create, update, status_change, etc.
    instance: Django model instance being audited
    diff: optional field-level diff
    """

    AuditEvent.objects.create(
        actor=user,
        action=action,
        object_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        diff=diff,
    )
