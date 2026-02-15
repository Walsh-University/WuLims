from django.db import migrations

ROLE_PERMISSIONS = {
    "Lab Tech": {
        ("samples", "view_sample"),
        ("results", "view_result"),
    },
    "Analyst": {
        ("samples", "view_sample"),
        ("samples", "change_sample"),
        ("results", "view_result"),
        ("results", "change_result"),
    },
    "QA Reviewer": {
        ("samples", "view_sample"),
        ("samples", "approve_sample"),
        ("results", "view_result"),
        ("results", "approve_result"),
        ("results", "reject_result"),

    },
    "Lab Manager": {
        ("samples", "view_sample"),
        ("samples", "add_sample"),
        ("samples", "change_sample"),
        ("samples", "delete_sample"),
        ("samples", "approve_sample"),
        ("results", "view_result"),
        ("results", "add_result"),
        ("results", "change_result"),
        ("results", "delete_result"),
        ("results", "approve_result"),
        ("results", "reject_result"),
    },
    "Customer Contact": {
        ("samples", "view_sample"),
        ("results", "view_result"),
    },
    "System Admin": {
        ("accounts", "manage_roles"),
        ("samples", "view_sample"),
        ("samples", "add_sample"),
        ("samples", "change_sample"),
        ("samples", "delete_sample"),
        ("samples", "approve_sample"),
        ("results", "view_result"),
        ("results", "add_result"),
        ("results", "change_result"),
        ("results", "delete_result"),
        ("results", "approve_result"),
        ("results", "reject_result"),

    },
}


def sync_roles(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")
    content_types = {
        "accounts": ContentType.objects.get_or_create(app_label="accounts", model="user")[0],
        "samples": ContentType.objects.get_or_create(app_label="samples", model="sample")[0],
        "results": ContentType.objects.get_or_create(app_label="results", model="result")[0],
    }

    for role_name, permission_refs in ROLE_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=role_name)
        permission_ids = []
        for app_label, codename in permission_refs:
            permission_ids.append(Permission.objects.get(content_type=content_types[app_label], codename=codename).id)
        group.permissions.set(permission_ids)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_sync_baseline_role_permissions"),
        ("results", "0003_alter_result_options")
    ]

    operations = [
        migrations.RunPython(sync_roles, reverse_code=migrations.RunPython.noop),
    ]
