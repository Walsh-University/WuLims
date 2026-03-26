# This will have a bridge to existing customers and person models.
from django.conf import settings
from django.db import models

from customers.models import Customer


class CustomerContact(models.Model):
    TITLE_CHOICES = [
        ("Mr", "Mr"),
        ("Mrs", "Mrs"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_contact",
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="contacts")

    title = models.CharField(
        max_length=10,
        choices=TITLE_CHOICES,
    )

    job_title = models.CharField(
        max_length=120,
        blank=True,
    )

    active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


# This will be something to enforce tenant boundaries
class CustomerMembership(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.customer.customer_name)


# This is how customers will "initiate" a project.
class ProjectRequest(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.customer.customer_name)
