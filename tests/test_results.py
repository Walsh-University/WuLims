"""Tests for the Result model."""

import pytest
from assertpy import assert_that
from django.core.exceptions import ValidationError
from django.urls import reverse
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
            "DRAFT",
            "IN_PROGRESS",
            "IN_REVIEW",
            "APPROVED",
            "REJECTED",
            "RELEASED",
        )

    def test_create_result_with_defaults(self, db, sample, project):
        """Result can be created in DRAFT state with no decision fields."""
        result = Result.objects.create(
            title="ICP-MS Readout",
            description="Initial acquisition completed.",
            sample=sample,
            project=project,
        )

        assert_that(result.status).is_equal_to(Result.Status.DRAFT)
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


class TestResultListView:
    """Tests for the result list page."""

    def test_list_requires_login(self, client):
        response = client.get(reverse("results:list"))

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).contains("login")

    def test_list_accessible_when_authenticated(self, authenticated_client):
        response = authenticated_client.get(reverse("results:list"))

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).contains("Results")


class TestResultTableView:
    """Tests for the HTMX result table endpoint."""

    def test_table_requires_login(self, client):
        response = client.get(reverse("results:table"))

        assert_that(response.status_code).is_equal_to(302)

    def test_table_returns_results(self, authenticated_client, sample, project):
        result = Result.objects.create(
            title="Lead Panel",
            description="Initial acquisition",
            sample=sample,
            project=project,
        )

        response = authenticated_client.get(reverse("results:table"))
        content = response.content.decode()

        assert_that(response.status_code).is_equal_to(200)
        assert_that(content).contains(str(result.id))
        assert_that(content).contains(project.name)
        assert_that(content).contains(str(sample.client_name))

    def test_table_filters_by_status(self, authenticated_client, sample, project, reviewer_user):
        draft = Result.objects.create(
            title="DRAFT Result",
            description="A",
            sample=sample,
            project=project,
            status=Result.Status.DRAFT,
        )
        in_review = Result.objects.create(
            title="Review Result",
            description="B",
            sample=sample,
            project=project,
            status=Result.Status.IN_REVIEW,
            reviewer=reviewer_user,
        )

        response = authenticated_client.get(reverse("results:table"), {"status": Result.Status.IN_REVIEW})
        content = response.content.decode()

        assert_that(response.status_code).is_equal_to(200)
        assert_that(content).contains(f"results-row-{in_review.id}")
        assert_that(content).does_not_contain(f"results-row-{draft.id}")

    def test_table_filters_by_search_query(self, authenticated_client, sample):
        project_alpha = sample.project
        project_alpha.name = "Alpha Project"
        project_alpha.save(update_fields=["name"])
        project_beta = type(project_alpha).objects.create(name="Beta Project", start_date="2026-01-10")
        beta_sample = type(sample).objects.create(
            sample_name="Beta Sample",
            project=project_beta,
            client_name="Beta Client",
        )

        alpha_result = Result.objects.create(
            title="Alpha Result",
            description="A",
            sample=sample,
            project=project_alpha,
        )
        beta_result = Result.objects.create(
            title="Beta Result",
            description="B",
            sample=beta_sample,
            project=project_beta,
        )

        response = authenticated_client.get(reverse("results:table"), {"q": "Alpha"})
        content = response.content.decode()

        assert_that(response.status_code).is_equal_to(200)
        assert_that(content).contains(f"results-row-{alpha_result.id}")
        assert_that(content).does_not_contain(f"results-row-{beta_result.id}")

    def test_table_invalid_status_does_not_crash(self, authenticated_client, sample, project):
        result = Result.objects.create(
            title="Stable Result",
            description="Validation should fail but response should render.",
            sample=sample,
            project=project,
        )

        response = authenticated_client.get(reverse("results:table"), {"status": "INVALID"})
        content = response.content.decode()

        assert_that(response.status_code).is_equal_to(200)
        assert_that(content).contains(str(result.id))


class TestResultAddView:
    """Tests for result creation."""

    def test_add_requires_login(self, client):
        response = client.get(reverse("results:add"))

        assert_that(response.status_code).is_equal_to(302)

    def test_add_renders_form_when_authenticated(self, manager_client):
        response = manager_client.get(reverse("results:add"))

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).contains("Add Result")

    def test_add_creates_result_and_redirects(self, manager_client, sample, project):
        response = manager_client.post(
            reverse("results:add"),
            {
                "project": project.pk,
                "sample": sample.pk,
                "title": "Created via Test",
                "description": "Created from add view post",
                "status": Result.Status.DRAFT,
            },
        )

        result = Result.objects.get(title="Created via Test")
        assert_that(result.project).is_equal_to(project)
        assert_that(result.sample).is_equal_to(sample)

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).is_equal_to(reverse("results:detail", args=[result.pk]))

    def test_add_invalid_payload_re_renders_form(self, manager_client, sample, project):
        response = manager_client.post(
            reverse("results:add"),
            {
                "project": project.pk,
                "sample": sample.pk,
                "title": "",
                "description": "Missing title",
                "status": Result.Status.DRAFT,
            },
        )

        assert_that(response.status_code).is_equal_to(200)
        assert_that(Result.objects.filter(description="Missing title").exists()).is_false()


class TestResultDetailView:
    """Tests for result detail and partial rendering."""

    def test_detail_requires_login(self, client, sample, project):
        result = Result.objects.create(
            title="Login Required",
            description="D",
            sample=sample,
            project=project,
        )
        response = client.get(reverse("results:detail", args=[result.pk]))

        assert_that(response.status_code).is_equal_to(302)

    def test_detail_returns_result(self, authenticated_client, sample, project):
        result = Result.objects.create(
            title="Detail Result",
            description="D",
            sample=sample,
            project=project,
        )
        response = authenticated_client.get(reverse("results:detail", args=[result.pk]))

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).contains("Result")
        assert_that(response.content.decode()).contains(str(result.id))

    def test_detail_404_for_missing_result(self, authenticated_client):
        response = authenticated_client.get(reverse("results:detail", args=[999999]))

        assert_that(response.status_code).is_equal_to(404)

    def test_detail_overview_tab_returns_partial(self, authenticated_client, sample, project):
        result = Result.objects.create(
            title="Overview Result",
            description="Overview Description",
            sample=sample,
            project=project,
        )

        response = authenticated_client.get(reverse("results:result_detail_tab", args=[result.pk]), {"tab": "overview"})
        content = response.content.decode()

        assert_that(response.status_code).is_equal_to(200)
        assert_that(content).contains("Overview Result")
        assert_that(content).contains("Overview Description")


class TestApproveModalView:
    """Tests for approve modal endpoint."""

    def test_approve_modal_requires_login(self, client, sample, project, reviewer_user):
        result = Result.objects.create(
            title="Approve Modal",
            description="Modal test",
            sample=sample,
            project=project,
            status=Result.Status.IN_REVIEW,
            reviewer=reviewer_user,
        )
        response = client.get(reverse("results:approve_modal", args=[result.pk]))

        assert_that(response.status_code).is_equal_to(302)

    def test_approve_modal_renders(self, reviewer_client, sample, project, reviewer_user):
        result = Result.objects.create(
            title="Approve Modal",
            description="Modal test",
            sample=sample,
            project=project,
            status=Result.Status.IN_REVIEW,
            reviewer=reviewer_user,
        )
        response = reviewer_client.get(reverse("results:approve_modal", args=[result.pk]))

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).contains(f"Review Result {result.id}")


class TestSubmitResultView:
    """Tests for submit-for-review flow."""

    def test_submit_requires_login(self, client, sample, project):
        result = Result.objects.create(
            title="Draft Result",
            description="Ready for review",
            sample=sample,
            project=project,
            status=Result.Status.DRAFT,
        )

        response = client.post(reverse("results:submit", args=[result.pk]))

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).contains("login")

    def test_submit_requires_post(self, manager_client, sample, project):
        result = Result.objects.create(
            title="Draft Result",
            description="Ready for review",
            sample=sample,
            project=project,
            status=Result.Status.DRAFT,
        )

        response = manager_client.get(reverse("results:submit", args=[result.pk]))

        assert_that(response.status_code).is_equal_to(400)
        assert_that(response.content.decode()).contains("POST required")

    def test_submit_requires_draft_status(self, manager_client, sample, project, reviewer_user):
        result = Result.objects.create(
            title="Already in Review",
            description="Cannot re-submit",
            sample=sample,
            project=project,
            status=Result.Status.IN_REVIEW,
            reviewer=reviewer_user,
        )

        response = manager_client.post(reverse("results:submit", args=[result.pk]))

        assert_that(response.status_code).is_equal_to(400)
        assert_that(response.content.decode()).contains("Result must be DRAFT")

    def test_submit_assigns_selected_reviewer(self, manager_client, sample, project, reviewer_user):
        result = Result.objects.create(
            title="Draft Result",
            description="Ready for review",
            sample=sample,
            project=project,
            status=Result.Status.DRAFT,
        )

        response = manager_client.post(
            reverse("results:submit", args=[result.pk]),
            {"reviewer_id": str(reviewer_user.pk)},
        )
        result.refresh_from_db()

        assert_that(response.status_code).is_equal_to(200)
        assert_that(result.status).is_equal_to(Result.Status.IN_REVIEW)
        assert_that(result.reviewer).is_equal_to(reviewer_user)

    def test_submit_auto_assigns_reviewer_when_not_provided(self, manager_client, sample, project, reviewer_user):
        result = Result.objects.create(
            title="Draft Result",
            description="Ready for review",
            sample=sample,
            project=project,
            status=Result.Status.DRAFT,
        )

        response = manager_client.post(reverse("results:submit", args=[result.pk]), {})
        result.refresh_from_db()

        assert_that(response.status_code).is_equal_to(200)
        assert_that(result.status).is_equal_to(Result.Status.IN_REVIEW)
        assert_that(result.reviewer).is_equal_to(reviewer_user)

    def test_submit_requires_eligible_reviewer(self, manager_client, sample, project):
        result = Result.objects.create(
            title="Draft Result",
            description="Ready for review",
            sample=sample,
            project=project,
            status=Result.Status.DRAFT,
        )

        response = manager_client.post(reverse("results:submit", args=[result.pk]), {})
        result.refresh_from_db()

        assert_that(response.status_code).is_equal_to(400)
        assert_that(response.content.decode()).contains("No eligible reviewer")
        assert_that(result.status).is_equal_to(Result.Status.DRAFT)

    def test_submit_validates_required_fields(self, manager_client, sample, project, reviewer_user):
        result = Result.objects.create(
            title="Draft Result",
            description="Ready for review",
            sample=sample,
            project=project,
            status=Result.Status.DRAFT,
        )
        Result.objects.filter(pk=result.pk).update(title=" ")

        response = manager_client.post(
            reverse("results:submit", args=[result.pk]),
            {"reviewer_id": str(reviewer_user.pk)},
        )
        result.refresh_from_db()

        assert_that(response.status_code).is_equal_to(400)
        assert_that(response.content.decode()).contains("Missing required fields")
        assert_that(result.status).is_equal_to(Result.Status.DRAFT)

    def test_submit_validates_missing_description(self, manager_client, sample, project, reviewer_user):
        result = Result.objects.create(
            title="Draft Result",
            description="Ready for review",
            sample=sample,
            project=project,
            status=Result.Status.DRAFT,
        )
        Result.objects.filter(pk=result.pk).update(description=" ")

        response = manager_client.post(
            reverse("results:submit", args=[result.pk]),
            {"reviewer_id": str(reviewer_user.pk)},
        )

        assert_that(response.status_code).is_equal_to(400)
        assert_that(response.content.decode()).contains("description")


class TestSubmitModalView:
    def test_submit_modal_requires_login(self, client, sample, project):
        result = Result.objects.create(
            title="Draft Result",
            description="Ready for review",
            sample=sample,
            project=project,
            status=Result.Status.DRAFT,
        )
        response = client.get(reverse("results:submit_modal", args=[result.pk]))
        assert_that(response.status_code).is_equal_to(302)

    def test_submit_modal_renders_for_draft(self, manager_client, sample, project):
        result = Result.objects.create(
            title="Draft Result",
            description="Ready for review",
            sample=sample,
            project=project,
            status=Result.Status.DRAFT,
        )
        response = manager_client.get(reverse("results:submit_modal", args=[result.pk]))
        assert_that(response.status_code).is_equal_to(200)

    def test_submit_modal_rejects_non_draft(self, manager_client, sample, project, reviewer_user):
        result = Result.objects.create(
            title="In Review",
            description="Already submitted",
            sample=sample,
            project=project,
            status=Result.Status.IN_REVIEW,
            reviewer=reviewer_user,
        )
        response = manager_client.get(reverse("results:submit_modal", args=[result.pk]))
        assert_that(response.status_code).is_equal_to(400)


class TestApproveModalForbidden:
    def test_approve_modal_forbidden_without_perms(self, authenticated_client, sample, project, reviewer_user):
        result = Result.objects.create(
            title="In Review",
            description="Awaiting decision",
            sample=sample,
            project=project,
            status=Result.Status.IN_REVIEW,
            reviewer=reviewer_user,
        )
        # authenticated_client is a Lab Tech with only view_result — no approve/reject
        response = authenticated_client.get(reverse("results:approve_modal", args=[result.pk]))
        assert_that(response.status_code).is_equal_to(403)


class TestApproveResultView:
    def test_approve_result_requires_post(self, reviewer_client, sample, project, reviewer_user):
        result = Result.objects.create(
            title="In Review",
            description="Awaiting approval",
            sample=sample,
            project=project,
            status=Result.Status.IN_REVIEW,
            reviewer=reviewer_user,
        )
        response = reviewer_client.get(reverse("results:approve", args=[result.pk]))
        assert_that(response.status_code).is_equal_to(400)

    def test_approve_result_rejects_non_in_review(self, reviewer_client, sample, project):
        result = Result.objects.create(
            title="Draft",
            description="Not ready",
            sample=sample,
            project=project,
            status=Result.Status.DRAFT,
        )
        response = reviewer_client.post(reverse("results:approve", args=[result.pk]))
        assert_that(response.status_code).is_equal_to(400)
        assert_that(response.content.decode()).contains("IN_REVIEW")

    def test_approve_result_transitions_to_approved(self, reviewer_client, sample, project, reviewer_user):
        result = Result.objects.create(
            title="In Review",
            description="Awaiting approval",
            sample=sample,
            project=project,
            status=Result.Status.IN_REVIEW,
            reviewer=reviewer_user,
        )
        response = reviewer_client.post(reverse("results:approve", args=[result.pk]))
        result.refresh_from_db()

        assert_that(response.status_code).is_equal_to(200)
        assert_that(result.status).is_equal_to(Result.Status.APPROVED)
        assert_that(result.approved_at).is_not_none()


class TestRejectResultView:
    def test_reject_result_requires_post(self, reviewer_client, sample, project, reviewer_user):
        result = Result.objects.create(
            title="In Review",
            description="Awaiting decision",
            sample=sample,
            project=project,
            status=Result.Status.IN_REVIEW,
            reviewer=reviewer_user,
        )
        response = reviewer_client.get(reverse("results:reject", args=[result.pk]))
        assert_that(response.status_code).is_equal_to(400)

    def test_reject_result_rejects_non_in_review(self, reviewer_client, sample, project):
        result = Result.objects.create(
            title="Draft",
            description="Not ready",
            sample=sample,
            project=project,
            status=Result.Status.DRAFT,
        )
        response = reviewer_client.post(reverse("results:reject", args=[result.pk]))
        assert_that(response.status_code).is_equal_to(400)
        assert_that(response.content.decode()).contains("IN_REVIEW")

    def test_reject_result_transitions_to_rejected(self, reviewer_client, sample, project, reviewer_user):
        result = Result.objects.create(
            title="In Review",
            description="Awaiting decision",
            sample=sample,
            project=project,
            status=Result.Status.IN_REVIEW,
            reviewer=reviewer_user,
        )
        response = reviewer_client.post(reverse("results:reject", args=[result.pk]))
        result.refresh_from_db()

        assert_that(response.status_code).is_equal_to(200)
        assert_that(result.status).is_equal_to(Result.Status.REJECTED)
        assert_that(result.rejected_at).is_not_none()


class TestReleaseResultView:
    def test_release_requires_release_permission(self, reviewer_client, sample, project, reviewer_user):
        result = Result.objects.create(
            title="Approved Result",
            description="Ready to release",
            sample=sample,
            project=project,
            status=Result.Status.APPROVED,
            approved_at=timezone.now(),
            approved_by=reviewer_user,
            reviewer=reviewer_user,
        )

        response = reviewer_client.post(reverse("results:release", args=[result.pk]))

        assert_that(response.status_code).is_equal_to(403)

    def test_release_requires_post(self, manager_client, sample, project, manager_user):
        result = Result.objects.create(
            title="Approved Result",
            description="Ready to release",
            sample=sample,
            project=project,
            status=Result.Status.APPROVED,
            approved_at=timezone.now(),
            approved_by=manager_user,
        )

        response = manager_client.get(reverse("results:release", args=[result.pk]))

        assert_that(response.status_code).is_equal_to(400)
        assert_that(response.content.decode()).contains("POST required")

    def test_release_requires_approved_status(self, manager_client, sample, project):
        result = Result.objects.create(
            title="Draft Result",
            description="Not approved",
            sample=sample,
            project=project,
            status=Result.Status.DRAFT,
        )

        response = manager_client.post(reverse("results:release", args=[result.pk]))
        result.refresh_from_db()

        assert_that(response.status_code).is_equal_to(400)
        assert_that(response.content.decode()).contains("Result must be APPROVED")
        assert_that(result.status).is_equal_to(Result.Status.DRAFT)

    def test_release_transitions_approved_to_released(
        self, manager_client, sample, project, reviewer_user, manager_user
    ):
        result = Result.objects.create(
            title="Approved Result",
            description="Ready to release",
            sample=sample,
            project=project,
            status=Result.Status.APPROVED,
            approved_at=timezone.now(),
            approved_by=reviewer_user,
            reviewer=reviewer_user,
        )

        response = manager_client.post(reverse("results:release", args=[result.pk]), HTTP_HX_REQUEST="true")
        result.refresh_from_db()

        assert_that(response.status_code).is_equal_to(200)
        assert_that(result.status).is_equal_to(Result.Status.RELEASED)
        assert_that(result.released_at).is_not_none()
        assert_that(result.released_by).is_equal_to(manager_user)

    def test_released_result_is_read_only(self, db, sample, project, reviewer_user, manager_user):
        result = Result.objects.create(
            title="Approved Result",
            description="Ready to release",
            sample=sample,
            project=project,
            status=Result.Status.APPROVED,
            approved_at=timezone.now(),
            approved_by=reviewer_user,
            reviewer=reviewer_user,
        )
        result.status = Result.Status.RELEASED
        result.released_at = timezone.now()
        result.released_by = manager_user
        result.save()

        result.description = "Changed after release"
        with pytest.raises(ValidationError) as exc:
            result.save()

        assert_that(exc.value.message_dict).contains_key("status")


class TestResultDetailTabAudit:
    def test_audit_tab_returns_200(self, authenticated_client, sample, project):
        result = Result.objects.create(
            title="Audit Tab Test",
            description="Testing audit tab",
            sample=sample,
            project=project,
        )
        response = authenticated_client.get(reverse("results:result_detail_tab", args=[result.pk]), {"tab": "audit"})
        assert_that(response.status_code).is_equal_to(200)
