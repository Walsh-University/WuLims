from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models

from audit.models import AuditEvent

User = get_user_model()


def get_system_user():
    user, _ = User.objects.get_or_create(username="system")
    return user


def log_audit_event(*, user=None, action: str, instance: models.Model, diff: dict[str, Any] | None = None) -> None:
    actor = user or get_system_user()

    AuditEvent.objects.create(
        actor=actor,
        action=action,
        object_type=ContentType.objects.get_for_model(instance),
        object_id=str(instance.pk),
        changes=diff,
    )
