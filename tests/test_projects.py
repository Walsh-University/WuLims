"""Tests for the projects app."""

from assertpy import assert_that

from projects.models import Project


class TestProjectsModel:
    """Tests for the Projects model."""

    def test_create_project(self, db, customer):
        """Project can be created with required fields."""
        project = Project.objects.create(
            name="Test",
            start_date="2026-01-01",
            description="description",
            status="ACTIVE",
            completed_date="2026-01-02",
            customer_id=customer,
        )
        assert_that(project.name).is_equal_to("Test")
        assert_that(project.start_date).is_equal_to("2026-01-01")
        assert_that(project.description).is_equal_to("description")
        assert_that(project.status).is_equal_to("ACTIVE")
        assert_that(project.completed_date).is_equal_to("2026-01-02")
        assert_that(project.created_at).is_not_none()
        assert_that(project.customer_id).is_equal_to(customer)

    def test_create_project_with_nullable_values(self, db):
        """Project creates expected null values when not provided."""
        project = Project.objects.create(
            name="Test",
            start_date="2026-01-01",
        )
        assert_that(project.description).is_empty()
        assert_that(project.completed_date).is_none()

    def test_project_default_values(self, db):
        """Project creates expected default values."""
        project = Project.objects.create(
            name="Test",
            start_date="2026-01-01",
        )
        assert_that(project.status).is_equal_to("ACTIVE")
        assert_that(project.created_at).is_not_none()
        assert_that(project.id).is_not_none()
