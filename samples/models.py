import uuid

from django.conf import settings
from django.db import models


class Sample(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "RECEIVED"
        IN_PROGRESS = "IN_PROGRESS"
        IN_REVIEW = "IN_REVIEW"
        APPROVED = "APPROVED"
        REJECTED = "REJECTED"

    class Filtration(models.TextChoices):
        DONE = "Done"
        NOT_NEEDED = "Not Needed"
        LAB_TO_DO = "Lab to do"

    class Preservation(models.TextChoices):
        LAB_TO_DO = "Lab to do"

    sample_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sample_name = models.CharField(max_length=255)
    project = models.ForeignKey("projects.Project", null=True, on_delete=models.PROTECT, related_name="samples")
    client_name = models.CharField(max_length=200)
    filtration = models.CharField(max_length=20, choices=Filtration.choices, default=Filtration.LAB_TO_DO)
    preservation = models.CharField(max_length=20, choices=Preservation.choices, default=Preservation.LAB_TO_DO)
    received_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECEIVED)

    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        permissions = [
            ("approve_sample", "Can approve sample"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    filtration__in=[
                        "Done",
                        "Not Needed",
                        "Lab to do",
                    ]
                ),
                name="sample_filtration_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(preservation="Lab to do"),
                name="sample_preservation_valid",
            ),
        ]

    def __str__(self):
        return str(self.sample_id)


class AnalysisType(models.Model):
    analysis_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class SampleAnalysis(models.Model):
    sample_analysis_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sample = models.ForeignKey("samples.Sample", on_delete=models.CASCADE, related_name="analyses")
    analysis_type = models.ForeignKey("samples.AnalysisType", on_delete=models.PROTECT, related_name="sample_analyses")
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["sample", "analysis_type"], name="uniq_sample_analysis_type"),
        ]
        ordering = ["-requested_at"]

    def __str__(self):
        return f"{self.sample_id} - {self.analysis_type.name}"
