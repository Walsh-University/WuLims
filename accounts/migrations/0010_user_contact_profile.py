from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customers", "0005_customeraddresses"),
        ("accounts", "0009_user_customer_profile"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="contact_profile",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="portal_user",
                to="customers.person",
            ),
        ),
    ]
