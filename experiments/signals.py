from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from audit.services import log_audit_event
from audit.diff import compute_diff
from audit.middleware import get_current_user

from .models import Experiment


AUDITED_FIELDS = [
    "name",
    "description",
    "status",
    "data_file",
    "version",
    "project",  # FIXED
]


@receiver(pre_save, sender=Experiment)
def cache_old_instance(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = Experiment.objects.get(pk=instance.pk)
        except Experiment.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save, sender=Experiment)
def audit_experiment(sender, instance, created, **kwargs):
    user = get_current_user()

    if created:
        log_audit_event(
            user=user,
            action="create",
            instance=instance,
        )
        return

    old_instance = getattr(instance, "_old_instance", None)

    if not old_instance:
        return

    diff = compute_diff(
        old=old_instance,
        new=instance,
        fields=AUDITED_FIELDS,
    )

    if not diff:
        return

    # Handle status change separately
    if "status" in diff:
        log_audit_event(
            user=user,
            action="status_change",
            instance=instance,
            diff={"status": diff["status"]},
        )
        diff.pop("status")

    if diff:
        log_audit_event(
            user=user,
            action="update",
            instance=instance,
            diff=diff,
        )
