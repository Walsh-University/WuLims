"""Tests for the Result model."""

import pytest
from assertpy import assert_that
from django.core.exceptions import ValidationError
from django.utils import timezone

from results.models import Result


class TestResultModel:
    """Result model happy-path and validation edge cases."""

    def test_result_str_returns_id(self, db, sample, project):
        """String representation should be the model id."""
        result = Result.objects.create(
            title="String Test",
            description="Checking __str__ output.",
            sample=sample,
            project=project,
        )

        assert_that(str(result)).is_equal_to(str(result.id))

    def test_result_status_choices(self):
        """Model exposes the expected status options."""
        statuses = [choice[0] for choice in Result.Status.choices]

        assert_that(statuses).contains(
            "ACQUIRED",
            "IN_PROGRESS",
            "IN_REVIEW",
            "APPROVED",
            "REJECTED",
        )

    def test_create_result_with_defaults(self, db, sample, project):
        """Result can be created in ACQUIRED state with no decision fields."""
        result = Result.objects.create(
            title="ICP-MS Readout",
            description="Initial acquisition completed.",
            sample=sample,
            project=project,
        )

        assert_that(result.status).is_equal_to(Result.Status.ACQUIRED)
        assert_that(result.approved_at).is_none()
        assert_that(result.approved_by).is_none()
        assert_that(result.rejected_at).is_none()
        assert_that(result.rejected_by).is_none()

    def test_create_approved_result_success(self, db, sample, project, user):
        """APPROVED status requires and accepts approval fields."""
        approved_at = timezone.now()

        result = Result.objects.create(
            title="Final Assay",
            description="Final QA-approved assay result.",
            sample=sample,
            project=project,
            status=Result.Status.APPROVED,
            approved_at=approved_at,
            approved_by=user,
        )

        assert_that(result.status).is_equal_to(Result.Status.APPROVED)
        assert_that(result.approved_at).is_equal_to(approved_at)
        assert_that(result.approved_by).is_equal_to(user)
        assert_that(user.approved_results.filter(pk=result.pk).exists()).is_true()

    def test_create_rejected_result_success(self, db, sample, project, user):
        """REJECTED status requires and accepts rejection fields."""
        rejected_at = timezone.now()

        result = Result.objects.create(
            title="Control Failure",
            description="Result rejected due to failed control sample.",
            sample=sample,
            project=project,
            status=Result.Status.REJECTED,
            rejected_at=rejected_at,
            rejected_by=user,
        )

        assert_that(result.status).is_equal_to(Result.Status.REJECTED)
        assert_that(result.rejected_at).is_equal_to(rejected_at)
        assert_that(result.rejected_by).is_equal_to(user)
        assert_that(user.rejected_results.filter(pk=result.pk).exists()).is_true()

    def test_approved_status_requires_approval_fields(self, db, sample, project):
        """APPROVED without approval fields is invalid."""
        with pytest.raises(ValidationError) as exc:
            Result.objects.create(
                title="Missing Approval Metadata",
                description="Should fail validation.",
                sample=sample,
                project=project,
                status=Result.Status.APPROVED,
            )

        message_dict = exc.value.message_dict
        assert_that(message_dict).contains_key("approved_at")
        assert_that(message_dict).contains_key("approved_by")

    def test_rejected_status_requires_rejection_fields(self, db, sample, project):
        """REJECTED without rejection fields is invalid."""
        with pytest.raises(ValidationError) as exc:
            Result.objects.create(
                title="Missing Rejection Metadata",
                description="Should fail validation.",
                sample=sample,
                project=project,
                status=Result.Status.REJECTED,
            )

        message_dict = exc.value.message_dict
        assert_that(message_dict).contains_key("rejected_at")
        assert_that(message_dict).contains_key("rejected_by")

    def test_non_terminal_status_rejects_approval_or_rejection_fields(self, db, sample, project, user):
        """Only APPROVED/REJECTED statuses may carry decision metadata."""
        with pytest.raises(ValidationError) as exc:
            Result.objects.create(
                title="In Review But Approved Fields Set",
                description="Should fail validation.",
                sample=sample,
                project=project,
                status=Result.Status.IN_REVIEW,
                approved_at=timezone.now(),
                approved_by=user,
            )

        assert_that(exc.value.message_dict).contains_key("approved_at")

        with pytest.raises(ValidationError) as exc2:
            Result.objects.create(
                title="In Progress But Rejected Fields Set",
                description="Should fail validation.",
                sample=sample,
                project=project,
                status=Result.Status.IN_PROGRESS,
                rejected_at=timezone.now(),
                rejected_by=user,
            )

        assert_that(exc2.value.message_dict).contains_key("rejected_at")

    def test_approved_status_cannot_include_rejected_fields(self, db, sample, project, user):
        """APPROVED status must not include rejected metadata."""
        with pytest.raises(ValidationError) as exc:
            Result.objects.create(
                title="Mixed Decision State",
                description="Should fail validation.",
                sample=sample,
                project=project,
                status=Result.Status.APPROVED,
                approved_at=timezone.now(),
                approved_by=user,
                rejected_at=timezone.now(),
                rejected_by=user,
            )

        assert_that(exc.value.message_dict).contains_key("status")

    def test_rejected_status_cannot_include_approved_fields(self, db, sample, project, user):
        """REJECTED status must not include approved metadata."""
        with pytest.raises(ValidationError) as exc:
            Result.objects.create(
                title="Mixed Decision State Reverse",
                description="Should fail validation.",
                sample=sample,
                project=project,
                status=Result.Status.REJECTED,
                rejected_at=timezone.now(),
                rejected_by=user,
                approved_at=timezone.now(),
                approved_by=user,
            )

        assert_that(exc.value.message_dict).contains_key("status")
