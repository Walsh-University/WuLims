from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customers", "0005_customeraddresses"),
        ("accounts", "0008_sync_baseline_role_permissions_customers"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="customer_profile",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="portal_users",
                to="customers.customer",
            ),
        ),
    ]
