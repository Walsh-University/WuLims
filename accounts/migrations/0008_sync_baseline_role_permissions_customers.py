from django.db import migrations

ROLE_PERMISSIONS = {
    "Lab Tech": {
        ("customers", "view_customer"),
        ("samples", "view_sample"),
        ("results", "view_result"),
    },
    "Analyst": {
        ("customers", "view_customer"),
        ("samples", "view_sample"),
        ("samples", "change_sample"),
        ("results", "view_result"),
        ("results", "change_result"),
        ("results", "submit_result"),
    },
    "QA Reviewer": {
        ("customers", "view_customer"),
        ("samples", "view_sample"),
        ("samples", "approve_sample"),
        ("results", "view_result"),
        ("results", "approve_result"),
        ("results", "reject_result"),
    },
    "Lab Manager": {
        ("customers", "view_customer"),
        ("customers", "add_customer"),
        ("customers", "change_customer"),
        ("customers", "delete_customer"),
        ("samples", "view_sample"),
        ("samples", "add_sample"),
        ("samples", "change_sample"),
        ("samples", "delete_sample"),
        ("samples", "approve_sample"),
        ("results", "view_result"),
        ("results", "add_result"),
        ("results", "change_result"),
        ("results", "submit_result"),
        ("results", "delete_result"),
        ("results", "approve_result"),
        ("results", "reject_result"),
        ("results", "release_result"),
    },
    "Customer Contact": {
        ("customers", "view_customer"),
        ("samples", "view_sample"),
        ("results", "view_result"),
    },
    "System Admin": {
        ("accounts", "manage_roles"),
        ("customers", "view_customer"),
        ("customers", "add_customer"),
        ("customers", "change_customer"),
        ("customers", "delete_customer"),
        ("samples", "view_sample"),
        ("samples", "add_sample"),
        ("samples", "change_sample"),
        ("samples", "delete_sample"),
        ("samples", "approve_sample"),
        ("results", "view_result"),
        ("results", "add_result"),
        ("results", "change_result"),
        ("results", "submit_result"),
        ("results", "delete_result"),
        ("results", "approve_result"),
        ("results", "reject_result"),
        ("results", "release_result"),
    },
}


def sync_roles(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")
    content_types = {
        "accounts": ContentType.objects.get_or_create(app_label="accounts", model="user")[0],
        "customers": ContentType.objects.get_or_create(app_label="customers", model="customer")[0],
        "samples": ContentType.objects.get_or_create(app_label="samples", model="sample")[0],
        "results": ContentType.objects.get_or_create(app_label="results", model="result")[0],
    }
    permission_names = {
        "manage_roles": "Can manage user role assignments",
        "view_customer": "Can view customer",
        "add_customer": "Can add customer",
        "change_customer": "Can change customer",
        "delete_customer": "Can delete customer",
        "view_sample": "Can view sample",
        "add_sample": "Can add sample",
        "change_sample": "Can change sample",
        "delete_sample": "Can delete sample",
        "approve_sample": "Can approve sample",
        "view_result": "Can view result",
        "add_result": "Can add result",
        "change_result": "Can change result",
        "submit_result": "Can submit result for review",
        "delete_result": "Can delete result",
        "approve_result": "Can approve result",
        "reject_result": "Can reject result",
        "release_result": "Can release approved result",
    }

    for role_name, permission_refs in ROLE_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=role_name)
        permission_ids = []
        for app_label, codename in permission_refs:
            perm, _ = Permission.objects.get_or_create(
                content_type=content_types[app_label],
                codename=codename,
                defaults={"name": permission_names[codename]},
            )
            permission_ids.append(perm.id)
        group.permissions.set(permission_ids)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0007_sync_baseline_role_permissions_release_result"),
        ("customers", "0003_personphonenumber"),
    ]

    operations = [
        migrations.RunPython(sync_roles, reverse_code=migrations.RunPython.noop),
    ]
