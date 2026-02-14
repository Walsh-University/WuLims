from django.db import models

from projects.models import Project


class Experiment(models.Model):
    class Status(models.TextChoices):
        CREATED = "CREATED"
        RUNNING = "RUNNING"
        COMPLETED = "COMPLETED"

    name = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)
    data_file = models.CharField(max_length=255)
    version = models.CharField(max_length=20)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.project})"
