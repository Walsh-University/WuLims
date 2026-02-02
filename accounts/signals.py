from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from accounts.audit import get_role_audit_actor
from accounts.models import RoleAssignmentAudit, User


def _clear_permission_caches(user: User) -> None:
    for cache_attr in ("_perm_cache", "_user_perm_cache", "_group_perm_cache"):
        if hasattr(user, cache_attr):
            delattr(user, cache_attr)


@receiver(m2m_changed, sender=User.groups.through)
def audit_role_assignment_changes(sender, instance, action, pk_set, **kwargs):
    actor = get_role_audit_actor()
    actor_id = actor.id if actor else None

    if action == "pre_clear":
        instance._role_audit_pre_clear_group_ids = set(instance.groups.values_list("id", flat=True))
        return

    if action == "post_add" and pk_set:
        groups = {g.id: g.name for g in instance.groups.model.objects.filter(id__in=pk_set)}
        RoleAssignmentAudit.objects.bulk_create(
            [
                RoleAssignmentAudit(
                    user=instance,
                    role_name=role_name,
                    action=RoleAssignmentAudit.Action.ASSIGNED,
                    changed_by_id=actor_id,
                )
                for role_name in groups.values()
            ]
        )
        _clear_permission_caches(instance)
        return

    if action == "post_remove" and pk_set:
        removed_groups = {g.id: g.name for g in instance.groups.model.objects.filter(id__in=pk_set)}
        RoleAssignmentAudit.objects.bulk_create(
            [
                RoleAssignmentAudit(
                    user=instance,
                    role_name=role_name,
                    action=RoleAssignmentAudit.Action.REMOVED,
                    changed_by_id=actor_id,
                )
                for role_name in removed_groups.values()
            ]
        )
        _clear_permission_caches(instance)
        return

    if action == "post_clear":
        removed_ids = getattr(instance, "_role_audit_pre_clear_group_ids", set())
        if removed_ids:
            removed_groups = {g.id: g.name for g in instance.groups.model.objects.filter(id__in=removed_ids)}
            RoleAssignmentAudit.objects.bulk_create(
                [
                    RoleAssignmentAudit(
                        user=instance,
                        role_name=role_name,
                        action=RoleAssignmentAudit.Action.REMOVED,
                        changed_by_id=actor_id,
                    )
                    for role_name in removed_groups.values()
                ]
            )
        _clear_permission_caches(instance)
        if hasattr(instance, "_role_audit_pre_clear_group_ids"):
            delattr(instance, "_role_audit_pre_clear_group_ids")
