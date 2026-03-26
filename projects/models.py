from django.db import models

from customer_portal.models import CustomerContact
from customers.models import Customer


class Project(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE"
        CLOSED = "CLOSED"

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    start_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name="customer")

    def __str__(self):
        return self.name

class ProjectRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        APPROVED = "APPROVED"
        REJECTED = "REJECTED"

    customer_contact = models.ForeignKey(
        CustomerContact,
        on_delete=models.CASCADE,
        related_name="project_requests"
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    business_context = models.TextField()
    scientific_context = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.status})"
