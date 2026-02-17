from django.db import migrations


def remove_legacy_result_permissions(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    result_ct = ContentType.objects.filter(app_label="results", model="result").first()
    if result_ct is None:
        return
    Permission.objects.filter(
        content_type=result_ct,
        codename__in=[
            "approve_experiment_result",
            "reject_experiment_result",
            "add_experiment_result",
        ],
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("results", "0003_alter_result_options"),
    ]

    operations = [
        migrations.RunPython(remove_legacy_result_permissions, reverse_code=migrations.RunPython.noop),
    ]
