from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from audit.diff import compute_diff
from audit.services import log_audit_event

from .models import Result

RESULT_FIELDS = [
    "title",
    "description",
    "status",
    "completed_at",
    "approved_at",
    "approved_by_id",
    "rejected_at",
    "rejected_by_id",
    "notes",
]


@receiver(pre_save, sender=Result)
def audit_result_update(sender, instance, **kwargs):
    if not instance.pk:
        return

    old_instance = Result.objects.get(pk=instance.pk)

    diff = compute_diff(
        old=old_instance,
        new=instance,
        fields=RESULT_FIELDS,
    )

    if diff:
        log_audit_event(
            user=None,
            action="update",
            instance=instance,
            diff=diff,
        )


@receiver(post_save, sender=Result)
def audit_result_create(sender, instance, created, **kwargs):
    if not created:
        return

    log_audit_event(
        user=None,
        action="create",
        instance=instance,
        diff=None,
    )


@receiver(post_delete, sender=Result)
def audit_result_delete(sender, instance, **kwargs):
    log_audit_event(
        user=None,
        action="delete",
        instance=instance,
        diff=None,
    )
