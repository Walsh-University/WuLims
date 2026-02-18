import uuid

from django.db import models


class Customer(models.Model):
    class Active(models.TextChoices):
        ACTIVE = "ACTIVE"
        INACTIVE = "INACTIVE"

    customer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_name = models.CharField(max_length=200)
    external_id = models.CharField(max_length=32, unique=True)
    customer_type = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.CharField(max_length=20, choices=Active.choices, default=Active.INACTIVE)

    def __str__(self):
        return self.customer_name


class Person(models.Model):
    class Title(models.TextChoices):
        MR = "MR"
        MS = "MS"
        MRS = "MRS"
        DR = "DR"

    person_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="people")
    title = models.CharField(max_length=10, choices=Title.choices, blank=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    suffix = models.CharField(max_length=50, blank=True)
    job_title = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    role_id = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
