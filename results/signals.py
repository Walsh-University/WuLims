from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from audit.diff import compute_diff
from audit.middleware import get_current_user
from audit.services import log_audit_event

from .models import Result

RESULT_FIELDS = [
    "title",
    "description",
    "status",
    "approved_at",
    "approved_by",
    "rejected_at",
    "rejected_by",
    "sample",
    "project",
]


@receiver(pre_save, sender=Result)
def cache_result_old_state(sender, instance, **kwargs):
    if not instance.pk:
        instance._audit_old_instance = None
        return

    instance._audit_old_instance = sender.objects.filter(pk=instance.pk).first()


@receiver(post_save, sender=Result)
def audit_result_save(sender, instance, created, **kwargs):

    if created:
        transaction.on_commit(
            lambda: log_audit_event(
                user=get_current_user(),
                action="create",
                instance=instance,
                diff=None,
            )
        )
        return

    old_instance = getattr(instance, "_audit_old_instance", None)
    if not old_instance:
        return

    diff = compute_diff(
        old=old_instance,
        new=instance,
        fields=RESULT_FIELDS,
    )

    if diff:
        transaction.on_commit(
            lambda: log_audit_event(
                user=get_current_user(),
                action="update",
                instance=instance,
                diff=diff,
            )
        )


@receiver(post_delete, sender=Result)
def audit_result_delete(sender, instance, **kwargs):
    transaction.on_commit(
        lambda: log_audit_event(
            user=get_current_user(),
            action="delete",
            instance=instance,
            diff=None,
        )
    )
