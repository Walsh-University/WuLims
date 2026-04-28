from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from audit.diff import compute_diff
from audit.middleware import get_current_user
from audit.services import log_audit_event

from .models import Person

PERSON_AUDIT_FIELDS = [
    "customer_id",
    "title",
    "first_name",
    "last_name",
    "job_title",
    "is_active",
]


@receiver(pre_save, sender=Person)
def cache_person_old_state(sender, instance, **kwargs):
    if not instance.pk:
        instance._audit_old_instance = None
        return

    instance._audit_old_instance = sender.objects.filter(pk=instance.pk).first()


@receiver(post_save, sender=Person)
def audit_person_save(sender, instance, created, **kwargs):
    if created:
        log_audit_event(
            user=get_current_user(),
            action="create",
            instance=instance,
            diff=None,
        )
        return

    old_instance = getattr(instance, "_audit_old_instance", None)
    if not old_instance:
        return

    diff = compute_diff(old=old_instance, new=instance, fields=PERSON_AUDIT_FIELDS)
    if diff:
        log_audit_event(
            user=get_current_user(),
            action="update",
            instance=instance,
            diff=diff,
        )
