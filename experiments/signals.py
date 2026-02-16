from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from audit.diff import compute_diff
from audit.services import log_audit_event

from .models import Experiment

EXPERIMENT_FIELDS = [
    "name",
    "description",
    "status",
    "data_file",
    "version",
]


# 🔹 UPDATE
@receiver(pre_save, sender=Experiment)
def audit_experiment_update(sender, instance, **kwargs):
    if not instance.pk:
        return  # это create

    old_instance = Experiment.objects.get(pk=instance.pk)

    diff = compute_diff(
        old=old_instance,
        new=instance,
        fields=EXPERIMENT_FIELDS,
    )

    if diff:
        log_audit_event(
            user=None,
            action="update",
            instance=instance,
            diff=diff,
        )


# 🔹 CREATE
@receiver(post_save, sender=Experiment)
def audit_experiment_create(sender, instance, created, **kwargs):
    if not created:
        return

    log_audit_event(
        user=None,
        action="create",
        instance=instance,
        diff=None,
    )


# 🔹 DELETE
@receiver(post_delete, sender=Experiment)
def audit_experiment_delete(sender, instance, **kwargs):
    log_audit_event(
        user=None,
        action="delete",
        instance=instance,
        diff=None,
    )
