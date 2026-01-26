from django.conf import settings
from django.db import models


class Customer(models.Model):

    class Active(models.TextChoices):
        ACTIVE = "ACTIVE"
        INACTIVE = "INACTIVE"

    customer_id = models.CharField(max_length=32, unique=True)
    customer_name = models.CharField(max_length=200)
    external_id = models.CharField(max_length=32, unique=True)
    customer_type = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.CharField(max_length=20, choices=Active.choices, default=Active.INACTIVE)



    def __str__(self):
        return self.customer_id