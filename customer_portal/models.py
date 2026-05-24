import uuid

from django.db import models

from customers.models import Customer, Person


# This will be something to enforce tenant boundaries
class CustomerMembership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="memberships")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Customer Memberships"

    def __str__(self):
        return str(self.customer.customer_name)


# This is how customers will "initiate" a project.
class ProjectRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="project_requests")
    requesting_contact = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="project_requests")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    business_context = models.TextField(help_text="Business context and objectives for this project")
    scientific_context = models.TextField(help_text="Scientific background and methodology")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Project Request {self.request_id} - {self.customer.customer_name}"
