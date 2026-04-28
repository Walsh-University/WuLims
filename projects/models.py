from django.db import models

from customers.models import Customer


class Project(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE"
        CLOSED = "CLOSED"

    class TurnaroundTime(models.TextChoices):
        STANDARD = "STANDARD", "Standard"
        RUSHED = "RUSHED", "Rushed"

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    turnaround_time = models.CharField(
        max_length=20,
        choices=TurnaroundTime.choices,
        default=TurnaroundTime.STANDARD,
    )
    start_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name="customer")

    def __str__(self):
        return self.name
