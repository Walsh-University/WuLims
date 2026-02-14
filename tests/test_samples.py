"""Tests for the samples app."""

import uuid

import pytest
from assertpy import assert_that
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.urls import reverse

from samples.models import AnalysisType, Sample, SampleAnalysis


class TestSampleModel:
    """Tests for the Sample model."""

    def test_create_sample(self, db, project):
        """Sample can be created with required fields."""
        sample = Sample.objects.create(
            sample_name="Drinking Water Grab",
            project=project,
            client_name="Acme Corp",
        )

        assert_that(sample.sample_id).is_instance_of(uuid.UUID)
        assert_that(sample.sample_name).is_equal_to("Drinking Water Grab")
        assert_that(sample.client_name).is_equal_to("Acme Corp")
        assert_that(sample.filtration).is_equal_to(Sample.Filtration.LAB_TO_DO)
        assert_that(sample.preservation).is_equal_to(Sample.Preservation.LAB_TO_DO)
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
                sample_name="Duplicate ID Sample",
                project=sample.project,
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

    def test_sample_approval_fields_nullable(self, db, project):
        """Approval fields are null by default."""
        sample = Sample.objects.create(
            sample_name="Approval Nullable Test",
            project=project,
            client_name="Test",
        )

        assert_that(sample.approved_at).is_none()
        assert_that(sample.approved_by).is_none()

    def test_sample_handling_rejects_invalid_values(self, db, project):
        sample = Sample(
            sample_name="Invalid Handling",
            project=project,
            client_name="Test",
            filtration="Unknown",
            preservation="Frozen",
        )

        with pytest.raises(ValidationError):
            sample.full_clean()


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

    def test_table_filters_by_search(self, authenticated_client, db, project):
        """Table can be filtered by search query."""
        Sample.objects.create(sample_name="Alpha Sample", project=project, client_name="Alpha Corp")
        Sample.objects.create(sample_name="Beta Sample", project=project, client_name="Beta Inc")

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

    def test_add_creates_sample_and_redirects(self, manager_client, db, project):
        """Valid post creates a sample and redirects to detail."""
        response = manager_client.post(
            reverse("samples:add"),
            {
                "sample_name": "Acme Sample",
                "project": project.pk,
                "client_name": "Acme Labs",
                "filtration": Sample.Filtration.DONE,
                "preservation": Sample.Preservation.LAB_TO_DO,
                "status": Sample.Status.RECEIVED,
            },
        )

        sample = Sample.objects.get(client_name="Acme Labs")
        assert_that(sample.project).is_equal_to(project)
        assert_that(sample.client_name).is_equal_to("Acme Labs")
        assert_that(sample.filtration).is_equal_to(Sample.Filtration.DONE)
        assert_that(sample.preservation).is_equal_to(Sample.Preservation.LAB_TO_DO)
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

    def test_add_creates_selected_analysis_types(self, manager_client, project):
        analysis_1 = AnalysisType.objects.create(code="METALS", name="Metals Panel", sort_order=1)
        analysis_2 = AnalysisType.objects.create(code="VOC", name="VOC Screen", sort_order=2)

        response = manager_client.post(
            reverse("samples:add"),
            {
                "sample_name": "Sample With Analyses",
                "project": project.pk,
                "client_name": "Acme Labs",
                "filtration": Sample.Filtration.NOT_NEEDED,
                "preservation": Sample.Preservation.LAB_TO_DO,
                "status": Sample.Status.RECEIVED,
                "analysis_types": [str(analysis_1.pk), str(analysis_2.pk)],
            },
        )

        sample = Sample.objects.get(sample_name="Sample With Analyses")
        selected_codes = set(sample.analyses.values_list("analysis_type__code", flat=True))
        assert_that(response.status_code).is_equal_to(302)
        assert_that(selected_codes).is_equal_to({"METALS", "VOC"})

    def test_add_rejects_invalid_filtration(self, manager_client, project):
        response = manager_client.post(
            reverse("samples:add"),
            {
                "sample_name": "Invalid Filtration Sample",
                "project": project.pk,
                "client_name": "Acme Labs",
                "filtration": "Bad Value",
                "preservation": Sample.Preservation.LAB_TO_DO,
                "status": Sample.Status.RECEIVED,
            },
        )

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).contains("Select a valid choice")
        assert_that(Sample.objects.filter(sample_name="Invalid Filtration Sample").exists()).is_false()


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

    def test_detail_shows_edit_button_with_permission(self, manager_client, sample):
        """Users with change_sample permission can see Edit action."""
        response = manager_client.get(reverse("samples:detail", args=[sample.pk]))

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).contains(reverse("samples:edit", args=[sample.pk]))

    def test_detail_hides_edit_button_without_permission(self, authenticated_client, sample):
        """Users without change_sample permission do not see Edit action."""
        response = authenticated_client.get(reverse("samples:detail", args=[sample.pk]))

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).does_not_contain(reverse("samples:edit", args=[sample.pk]))

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

    def test_detail_overview_shows_analysis_types(self, authenticated_client, sample):
        analysis = AnalysisType.objects.create(code="NUTRIENTS", name="Nutrients Panel")
        SampleAnalysis.objects.create(sample=sample, analysis_type=analysis)

        response = authenticated_client.get(
            reverse("samples:detail", args=[sample.pk]),
            {"tab": "overview"},
        )

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).contains("Nutrients Panel")

    def test_detail_overview_shows_sample_handling(self, authenticated_client, sample):
        sample.filtration = Sample.Filtration.DONE
        sample.preservation = Sample.Preservation.LAB_TO_DO
        sample.save(update_fields=["filtration", "preservation"])

        response = authenticated_client.get(
            reverse("samples:detail", args=[sample.pk]),
            {"tab": "overview"},
        )

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).contains(Sample.Filtration.DONE)
        assert_that(response.content.decode()).contains(Sample.Preservation.LAB_TO_DO)

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


class TestSampleEditView:
    """Tests for sample edit functionality."""

    def test_edit_requires_login(self, client, sample):
        response = client.get(reverse("samples:edit", args=[sample.pk]))

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).contains("login")

    def test_edit_forbidden_without_permission(self, authenticated_client, sample):
        response = authenticated_client.get(reverse("samples:edit", args=[sample.pk]))

        assert_that(response.status_code).is_equal_to(403)

    def test_edit_renders_form_for_manager(self, manager_client, sample):
        response = manager_client.get(reverse("samples:edit", args=[sample.pk]))

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).contains("Edit Sample")
        assert_that(response.content.decode()).contains(sample.sample_name)

    def test_edit_updates_sample_and_redirects(self, manager_client, sample, project):
        response = manager_client.post(
            reverse("samples:edit", args=[sample.pk]),
            {
                "sample_name": "Updated Sample Name",
                "project": project.pk,
                "client_name": "Updated Client",
                "filtration": Sample.Filtration.NOT_NEEDED,
                "preservation": Sample.Preservation.LAB_TO_DO,
                "status": Sample.Status.IN_PROGRESS,
                "approved_at": "",
                "approved_by": "",
            },
        )

        sample.refresh_from_db()
        assert_that(sample.sample_name).is_equal_to("Updated Sample Name")
        assert_that(sample.client_name).is_equal_to("Updated Client")
        assert_that(sample.filtration).is_equal_to(Sample.Filtration.NOT_NEEDED)
        assert_that(sample.preservation).is_equal_to(Sample.Preservation.LAB_TO_DO)
        assert_that(sample.status).is_equal_to(Sample.Status.IN_PROGRESS)
        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).is_equal_to(reverse("samples:detail", args=[sample.pk]))

    def test_edit_updates_analysis_types(self, manager_client, sample, project):
        analysis_1 = AnalysisType.objects.create(code="PH", name="pH")
        analysis_2 = AnalysisType.objects.create(code="TSS", name="Total Suspended Solids")
        analysis_3 = AnalysisType.objects.create(code="COD", name="Chemical Oxygen Demand")
        SampleAnalysis.objects.create(sample=sample, analysis_type=analysis_1)
        SampleAnalysis.objects.create(sample=sample, analysis_type=analysis_2)

        response = manager_client.post(
            reverse("samples:edit", args=[sample.pk]),
            {
                "sample_name": sample.sample_name,
                "project": project.pk,
                "client_name": sample.client_name,
                "filtration": Sample.Filtration.LAB_TO_DO,
                "preservation": Sample.Preservation.LAB_TO_DO,
                "status": sample.status,
                "approved_at": "",
                "approved_by": "",
                "analysis_types": [str(analysis_2.pk), str(analysis_3.pk)],
            },
        )

        sample.refresh_from_db()
        selected_codes = set(sample.analyses.values_list("analysis_type__code", flat=True))
        assert_that(response.status_code).is_equal_to(302)
        assert_that(selected_codes).is_equal_to({"TSS", "COD"})


class TestSampleRowActions:
    """Tests for sample row action rendering."""

    def test_table_row_shows_edit_action_with_permission(self, manager_client, sample):
        response = manager_client.get(reverse("samples:table"))

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).contains(reverse("samples:edit", args=[sample.pk]))

    def test_table_row_hides_edit_action_without_permission(self, authenticated_client, sample):
        response = authenticated_client.get(reverse("samples:table"))

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).does_not_contain(reverse("samples:edit", args=[sample.pk]))


class TestAnalysisTypeModel:
    """Tests for analysis type catalog model."""

    def test_create_analysis_type(self, db):
        analysis = AnalysisType.objects.create(code="VOC", name="Volatile Organics", sort_order=2)

        assert_that(analysis.analysis_type_id).is_instance_of(uuid.UUID)
        assert_that(analysis.code).is_equal_to("VOC")
        assert_that(analysis.name).is_equal_to("Volatile Organics")
        assert_that(analysis.is_active).is_true()

    def test_analysis_type_str(self, analysis_type):
        assert_that(str(analysis_type)).is_equal_to("Metals Panel")

    def test_analysis_type_code_unique(self, db):
        AnalysisType.objects.create(code="NUTRIENTS", name="Nutrients")

        with pytest.raises(IntegrityError):
            AnalysisType.objects.create(code="NUTRIENTS", name="Different Name")


class TestSampleAnalysisModel:
    """Tests for sample-to-analysis assignment model."""

    def test_create_sample_analysis(self, sample, analysis_type):
        sample_analysis = SampleAnalysis.objects.create(sample=sample, analysis_type=analysis_type)

        assert_that(sample_analysis.sample_analysis_id).is_instance_of(uuid.UUID)
        assert_that(sample_analysis.sample).is_equal_to(sample)
        assert_that(sample_analysis.analysis_type).is_equal_to(analysis_type)
        assert_that(sample_analysis.requested_at).is_not_none()

    def test_unique_sample_analysis_pair(self, sample, analysis_type):
        SampleAnalysis.objects.create(sample=sample, analysis_type=analysis_type)

        with pytest.raises(IntegrityError):
            SampleAnalysis.objects.create(sample=sample, analysis_type=analysis_type)

    def test_deleting_sample_cascades_sample_analysis(self, sample, analysis_type):
        sample_analysis = SampleAnalysis.objects.create(sample=sample, analysis_type=analysis_type)
        sample.delete()

        assert_that(SampleAnalysis.objects.filter(pk=sample_analysis.pk).exists()).is_false()

    def test_deleting_analysis_type_is_protected(self, sample, analysis_type):
        SampleAnalysis.objects.create(sample=sample, analysis_type=analysis_type)

        with pytest.raises(ProtectedError):
            analysis_type.delete()
