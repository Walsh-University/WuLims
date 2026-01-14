from django.db import models
from django.conf import settings

class Sample(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "RECEIVED"
        IN_PROGRESS = "IN_PROGRESS"
        IN_REVIEW = "IN_REVIEW"
        APPROVED = "APPROVED"
        REJECTED = "REJECTED"

    sample_id = models.CharField(max_length=32, unique=True)
    client_name = models.CharField(max_length=200)
    received_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECEIVED)

    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.sample_id
