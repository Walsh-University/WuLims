from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from audit.services import log_audit_event

from .models import Experiment


@receiver(post_save, sender=Experiment)
def audit_experiment_save(sender, instance, created, **kwargs):
    action = "create" if created else "update"
    log_audit_event(
        user=None,
        action=action,
        instance=instance,
        diff=None,
    )


@receiver(post_delete, sender=Experiment)
def audit_experiment_delete(sender, instance, **kwargs):
    log_audit_event(
        user=None,
        action="delete",
        instance=instance,
        diff=None,
    )
