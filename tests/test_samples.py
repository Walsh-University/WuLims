"""Tests for the samples app."""

import uuid

import pytest
from assertpy import assert_that
from django.db import IntegrityError
from django.urls import reverse

from samples.models import Sample


class TestSampleModel:
    """Tests for the Sample model."""

    def test_create_sample(self, db):
        """Sample can be created with required fields."""
        sample = Sample.objects.create(
            client_name="Acme Corp",
        )

        assert_that(sample.sample_id).is_instance_of(uuid.UUID)
        assert_that(sample.client_name).is_equal_to("Acme Corp")
        assert_that(sample.status).is_equal_to(Sample.Status.RECEIVED)
        assert_that(sample.received_at).is_not_none()

    def test_sample_str(self, sample):
        """Sample string representation is the sample_id."""
        assert_that(str(sample)).is_equal_to(str(sample.sample_id))

    def test_sample_id_unique(self, sample, db):
        """Sample IDs must be unique."""
        sample_id = sample.sample_id
        with pytest.raises(IntegrityError):
            Sample.objects.create(
                sample_id=sample_id,
                client_name="Different Client",
            )

    def test_sample_status_choices(self):
        """All expected status choices exist."""
        statuses = [choice[0] for choice in Sample.Status.choices]

        assert_that(statuses).contains(
            "RECEIVED",
            "IN_PROGRESS",
            "IN_REVIEW",
            "APPROVED",
            "REJECTED",
        )

    def test_sample_approval_fields_nullable(self, db):
        """Approval fields are null by default."""
        sample = Sample.objects.create(
            client_name="Test",
        )

        assert_that(sample.approved_at).is_none()
        assert_that(sample.approved_by).is_none()


class TestSampleListView:
    """Tests for the sample list view."""

    def test_list_requires_login(self, client):
        """Unauthenticated users are redirected to login."""
        response = client.get(reverse("samples:list"))

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).contains("login")

    def test_list_accessible_when_authenticated(self, authenticated_client):
        """Authenticated users can access the list."""
        response = authenticated_client.get(reverse("samples:list"))

        assert_that(response.status_code).is_equal_to(200)


class TestSampleTableView:
    """Tests for the sample table partial (HTMX endpoint)."""

    def test_table_requires_login(self, client):
        """Unauthenticated users are redirected."""
        response = client.get(reverse("samples:table"))

        assert_that(response.status_code).is_equal_to(302)

    def test_table_returns_samples(self, authenticated_client, sample):
        """Table view returns sample data."""
        response = authenticated_client.get(reverse("samples:table"))

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).contains(str(sample.sample_id))

    def test_table_filters_by_status(self, authenticated_client, sample, sample_in_review):
        """Table can be filtered by status."""
        response = authenticated_client.get(
            reverse("samples:table"),
            {"status": "IN_REVIEW"},
        )

        content = response.content.decode()
        assert_that(content).contains(str(sample_in_review.sample_id))
        assert_that(content).does_not_contain(str(sample.sample_id))

    def test_table_filters_by_search(self, authenticated_client, db):
        """Table can be filtered by search query."""
        Sample.objects.create(client_name="Alpha Corp")
        Sample.objects.create(client_name="Beta Inc")

        response = authenticated_client.get(
            reverse("samples:table"),
            {"q": "Alpha"},
        )

        content = response.content.decode()
        assert_that(content).contains("Alpha Corp")
        assert_that(content).does_not_contain("Beta Inc")


class TestSampleAddView:
    """Tests for the sample add view."""

    def test_add_requires_login(self, client):
        """Unauthenticated users are redirected to login."""
        response = client.get(reverse("samples:add"))

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).contains("login")

    def test_add_renders_form_for_authenticated_user(self, manager_client):
        """Authenticated users can access the add form."""
        response = manager_client.get(reverse("samples:add"))

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).contains("Add Sample")

    def test_add_creates_sample_and_redirects(self, manager_client, db):
        """Valid post creates a sample and redirects to detail."""
        response = manager_client.post(
            reverse("samples:add"),
            {"client_name": "Acme Labs", "status": Sample.Status.RECEIVED},
        )

        sample = Sample.objects.get(client_name="Acme Labs")
        assert_that(sample.client_name).is_equal_to("Acme Labs")
        assert_that(sample.status).is_equal_to(Sample.Status.RECEIVED)
        assert_that(sample.sample_id).is_instance_of(uuid.UUID)

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).is_equal_to(reverse("samples:detail", args=[sample.pk]))

    def test_add_forbidden_without_permission(self, viewer_client):
        """Users without add permission cannot access add form."""
        response = viewer_client.get(reverse("samples:add"))

        assert_that(response.status_code).is_equal_to(403)

    def test_add_forbidden_for_lab_tech(self, authenticated_client):
        """Lab Tech role is view-only and cannot add samples."""
        response = authenticated_client.get(reverse("samples:add"))

        assert_that(response.status_code).is_equal_to(403)


class TestSampleDetailView:
    """Tests for the sample detail view."""

    def test_detail_requires_login(self, client, sample):
        """Unauthenticated users are redirected."""
        response = client.get(reverse("samples:detail", args=[sample.pk]))

        assert_that(response.status_code).is_equal_to(302)

    def test_detail_returns_sample(self, authenticated_client, sample):
        """Detail view returns sample information."""
        response = authenticated_client.get(reverse("samples:detail", args=[sample.pk]))

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).contains(str(sample.sample_id))

    def test_detail_404_for_nonexistent(self, authenticated_client):
        """Returns 404 for nonexistent sample."""
        response = authenticated_client.get(reverse("samples:detail", args=[uuid.uuid4()]))

        assert_that(response.status_code).is_equal_to(404)

    def test_detail_overview_tab(self, authenticated_client, sample):
        """Overview tab returns partial."""
        response = authenticated_client.get(
            reverse("samples:detail", args=[sample.pk]),
            {"tab": "overview"},
        )

        assert_that(response.status_code).is_equal_to(200)

    def test_detail_coc_tab(self, authenticated_client, sample):
        """Chain of custody tab returns partial."""
        response = authenticated_client.get(
            reverse("samples:detail", args=[sample.pk]),
            {"tab": "coc"},
        )

        assert_that(response.status_code).is_equal_to(200)


class TestApproveSampleView:
    """Tests for sample approval functionality."""

    def test_approve_requires_login(self, client, sample_in_review):
        """Unauthenticated users cannot approve."""
        response = client.post(reverse("samples:approve", args=[sample_in_review.pk]))

        assert_that(response.status_code).is_equal_to(302)

    def test_approve_requires_post(self, reviewer_client, sample_in_review):
        """GET requests are rejected."""
        response = reviewer_client.get(reverse("samples:approve", args=[sample_in_review.pk]))

        assert_that(response.status_code).is_equal_to(400)

    def test_approve_requires_in_review_status(self, reviewer_client, sample):
        """Cannot approve sample not in IN_REVIEW status."""
        response = reviewer_client.post(reverse("samples:approve", args=[sample.pk]))

        assert_that(response.status_code).is_equal_to(400)
        assert_that(response.content.decode()).contains("IN_REVIEW")

    def test_approve_success(self, reviewer_client, sample_in_review, reviewer_user):
        """Sample can be approved when in IN_REVIEW status."""
        response = reviewer_client.post(reverse("samples:approve", args=[sample_in_review.pk]))

        assert_that(response.status_code).is_equal_to(200)

        sample_in_review.refresh_from_db()
        assert_that(sample_in_review.status).is_equal_to(Sample.Status.APPROVED)
        assert_that(sample_in_review.approved_at).is_not_none()
        assert_that(sample_in_review.approved_by).is_equal_to(reviewer_user)

    def test_approve_returns_updated_row(self, reviewer_client, sample_in_review):
        """Approval response includes updated row HTML."""
        response = reviewer_client.post(reverse("samples:approve", args=[sample_in_review.pk]))

        content = response.content.decode()
        assert_that(content).contains("APPROVED")

    def test_approve_returns_toast(self, reviewer_client, sample_in_review):
        """Approval response includes success toast."""
        response = reviewer_client.post(reverse("samples:approve", args=[sample_in_review.pk]))

        content = response.content.decode()
        assert_that(content).contains("approved")
        assert_that(content).contains("toast")

    def test_approve_forbidden_without_permission(self, authenticated_client, sample_in_review):
        """Users without approve permission receive forbidden."""
        response = authenticated_client.post(reverse("samples:approve", args=[sample_in_review.pk]))

        assert_that(response.status_code).is_equal_to(403)


class TestApproveModalView:
    """Tests for the approval modal endpoint."""

    def test_modal_requires_login(self, client, sample_in_review):
        """Unauthenticated users cannot access modal."""
        response = client.get(reverse("samples:approve_modal", args=[sample_in_review.pk]))

        assert_that(response.status_code).is_equal_to(302)

    def test_modal_returns_content(self, reviewer_client, sample_in_review):
        """Modal endpoint returns modal HTML."""
        response = reviewer_client.get(reverse("samples:approve_modal", args=[sample_in_review.pk]))

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).contains(str(sample_in_review.sample_id))

    def test_modal_forbidden_without_permission(self, authenticated_client, sample_in_review):
        """Users without approve permission cannot load modal."""
        response = authenticated_client.get(reverse("samples:approve_modal", args=[sample_in_review.pk]))

        assert_that(response.status_code).is_equal_to(403)
