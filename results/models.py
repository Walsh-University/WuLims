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
        RELEASED = "RELEASED"

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
    released_at = models.DateTimeField(null=True, blank=True)
    released_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="released_results",
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
            ("release_result", "Can release approved result"),
        ]

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        errors = {}
        old = type(self).objects.filter(pk=self.pk).first() if self.pk else None

        approved_fields_present = self.approved_at is not None or self.approved_by is not None
        rejected_fields_present = self.rejected_at is not None or self.rejected_by is not None
        released_fields_present = self.released_at is not None or self.released_by is not None

        if self.status == self.Status.APPROVED:
            if self.approved_at is None:
                errors["approved_at"] = "approved_at is required when status is APPROVED."
            if self.approved_by is None:
                errors["approved_by"] = "approved_by is required when status is APPROVED."
            if rejected_fields_present:
                errors["status"] = "Rejected fields must be empty when status is APPROVED."
            if released_fields_present:
                errors["status"] = "Released fields must be empty when status is APPROVED."

        if self.status == self.Status.REJECTED:
            if self.rejected_at is None:
                errors["rejected_at"] = "rejected_at is required when status is REJECTED."
            if self.rejected_by is None:
                errors["rejected_by"] = "rejected_by is required when status is REJECTED."
            if approved_fields_present:
                errors["status"] = "Approved fields must be empty when status is REJECTED."
            if released_fields_present:
                errors["status"] = "Released fields must be empty when status is REJECTED."

        if self.status == self.Status.RELEASED:
            if self.released_at is None:
                errors["released_at"] = "released_at is required when status is RELEASED."
            if self.released_by is None:
                errors["released_by"] = "released_by is required when status is RELEASED."
            if self.approved_at is None or self.approved_by is None:
                errors["status"] = "Result must be approved before it can be released."
            if rejected_fields_present:
                errors["status"] = "Rejected fields must be empty when status is RELEASED."

        if self.status not in {self.Status.APPROVED, self.Status.RELEASED, self.Status.REJECTED}:
            if approved_fields_present:
                errors["approved_at"] = "Approved fields must be empty unless status is APPROVED."
            if rejected_fields_present:
                errors["rejected_at"] = "Rejected fields must be empty unless status is REJECTED."
        if self.status != self.Status.RELEASED and released_fields_present:
            errors["released_at"] = "Released fields must be empty unless status is RELEASED."

        if self.status == self.Status.IN_REVIEW and self.reviewer is None:
            errors["reviewer"] = "reviewer is required when status is IN_REVIEW."

        if self.status in {self.Status.DRAFT, self.Status.IN_PROGRESS} and self.reviewer is not None:
            errors["reviewer"] = "reviewer must be empty unless status is IN_REVIEW or finalized."

        if old is not None:
            if old.status == self.Status.RELEASED:
                tracked_fields = (
                    "title",
                    "description",
                    "sample_id",
                    "project_id",
                    "completed_at",
                    "status",
                    "approved_at",
                    "approved_by_id",
                    "rejected_at",
                    "rejected_by_id",
                    "released_at",
                    "released_by_id",
                    "reviewer_id",
                    "notes",
                )
                if any(getattr(self, field) != getattr(old, field) for field in tracked_fields):
                    errors["status"] = "Released results are read-only."

            if self.status == self.Status.RELEASED and old.status != self.Status.APPROVED:
                errors["status"] = "Release transition must be APPROVED -> RELEASED."
        elif self.status == self.Status.RELEASED:
            errors["status"] = "Release transition must be APPROVED -> RELEASED."

        if errors:
            raise ValidationError(errors)
