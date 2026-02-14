from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Experiment
from audit.services import log_audit_event


def get_current_user():
    return None


@receiver(post_save, sender=Experiment)
def audit_experiment_save(sender, instance, created, **kwargs):
    action = "create" if created else "update"
    log_audit_event(user=get_current_user(), action=action, instance=instance, diff=None)


@receiver(post_delete, sender=Experiment)
def audit_experiment_delete(sender, instance, **kwargs):
    log_audit_event(user=get_current_user(), action="delete", instance=instance, diff=None)
