from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from projects.models import Project
from samples.models import Sample


class Result(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT"
        IN_PROGRESS = "IN_PROGRESS"
        IN_REVIEW = "IN_REVIEW"
        APPROVED = "APPROVED"
        REJECTED = "REJECTED"

    title = models.CharField(max_length=100)
    description = models.TextField()

    sample = models.ForeignKey(Sample, on_delete=models.PROTECT, related_name="samples")
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="projects")
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_results",
    )

    rejected_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="rejected_results",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="review_results",
    )

    notes = models.TextField(blank=True)

    class Meta:
        permissions = [
            ("submit_result", "Can submit result for review"),
            ("approve_result", "Can approve result"),
            ("reject_result", "Can reject result"),
        ]

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        errors = {}

        approved_fields_present = self.approved_at is not None or self.approved_by is not None
        rejected_fields_present = self.rejected_at is not None or self.rejected_by is not None

        if self.status == self.Status.APPROVED:
            if self.approved_at is None:
                errors["approved_at"] = "approved_at is required when status is APPROVED."
            if self.approved_by is None:
                errors["approved_by"] = "approved_by is required when status is APPROVED."
            if rejected_fields_present:
                errors["status"] = "Rejected fields must be empty when status is APPROVED."

        if self.status == self.Status.REJECTED:
            if self.rejected_at is None:
                errors["rejected_at"] = "rejected_at is required when status is REJECTED."
            if self.rejected_by is None:
                errors["rejected_by"] = "rejected_by is required when status is REJECTED."
            if approved_fields_present:
                errors["status"] = "Approved fields must be empty when status is REJECTED."

        if self.status not in {self.Status.APPROVED, self.Status.REJECTED}:
            if approved_fields_present:
                errors["approved_at"] = "Approved fields must be empty unless status is APPROVED."
            if rejected_fields_present:
                errors["rejected_at"] = "Rejected fields must be empty unless status is REJECTED."

        if self.status == self.Status.IN_REVIEW and self.reviewer is None:
            errors["reviewer"] = "reviewer is required when status is IN_REVIEW."

        if self.status in {self.Status.DRAFT, self.Status.IN_PROGRESS} and self.reviewer is not None:
            errors["reviewer"] = "reviewer must be empty unless status is IN_REVIEW or finalized."

        if errors:
            raise ValidationError(errors)
