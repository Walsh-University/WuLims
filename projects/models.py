from django.db import models


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
    # Remove comment once customers app is added
    # customer_id = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.id
