"""Tests for the projects app."""

from assertpy import assert_that
from django.urls import reverse

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


class TestProjectListView:
    """Tests for the project list page."""

    def test_list_requires_login(self, client):
        response = client.get(reverse("projects:list"))

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).contains("login")

    def test_list_forbidden_without_permission(self, authenticated_client):
        response = authenticated_client.get(reverse("projects:list"))

        assert_that(response.status_code).is_equal_to(403)

    def test_list_accessible_when_authorized(self, client, admin_user):
        client.force_login(admin_user)
        response = client.get(reverse("projects:list"))

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).contains("Projects")


class TestProjectTableView:
    """Tests for the project table partial endpoint."""

    def test_table_requires_login(self, client):
        response = client.get(reverse("projects:table"))

        assert_that(response.status_code).is_equal_to(302)

    def test_table_forbidden_without_permission(self, authenticated_client):
        response = authenticated_client.get(reverse("projects:table"))

        assert_that(response.status_code).is_equal_to(403)

    def test_table_returns_projects(self, client, admin_user, project):
        client.force_login(admin_user)
        response = client.get(reverse("projects:table"))

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).contains(project.name)

    def test_table_filters_by_status(self, client, admin_user, db):
        client.force_login(admin_user)
        active_project = Project.objects.create(name="Active Project", start_date="2026-01-01", status="ACTIVE")
        Project.objects.create(name="Closed Project", start_date="2026-01-02", status="CLOSED")

        response = client.get(reverse("projects:table"), {"status": "ACTIVE"})

        content = response.content.decode()
        assert_that(response.status_code).is_equal_to(200)
        assert_that(content).contains(active_project.name)
        assert_that(content).does_not_contain("Closed Project")

    def test_table_filters_by_search(self, client, admin_user, db):
        client.force_login(admin_user)
        Project.objects.create(name="Alpha Initiative", start_date="2026-01-01", description="Primary")
        Project.objects.create(name="Beta Initiative", start_date="2026-01-02", description="Secondary")

        response = client.get(reverse("projects:table"), {"q": "Alpha"})

        content = response.content.decode()
        assert_that(response.status_code).is_equal_to(200)
        assert_that(content).contains("Alpha Initiative")
        assert_that(content).does_not_contain("Beta Initiative")


class TestProjectAddView:
    """Tests for the project add view."""

    def test_add_requires_login(self, client):
        response = client.get(reverse("projects:add"))

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).contains("login")

    def test_add_forbidden_without_permission(self, authenticated_client):
        response = authenticated_client.get(reverse("projects:add"))

        assert_that(response.status_code).is_equal_to(403)

    def test_add_renders_form_when_authorized(self, client, admin_user):
        client.force_login(admin_user)
        response = client.get(reverse("projects:add"))

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.content.decode()).contains("Add Project")

    def test_add_creates_project_and_redirects(self, client, admin_user, customer):
        client.force_login(admin_user)
        response = client.post(
            reverse("projects:add"),
            {
                "name": "New Intake Project",
                "description": "Created from add form",
                "status": Project.Status.ACTIVE,
                "start_date": "2026-02-01",
                "completed_date": "",
                "customer_id": customer.pk,
            },
        )

        created = Project.objects.get(name="New Intake Project")
        assert_that(created.description).is_equal_to("Created from add form")
        assert_that(created.status).is_equal_to(Project.Status.ACTIVE)
        assert_that(str(created.start_date)).is_equal_to("2026-02-01")
        assert_that(created.completed_date).is_none()
        assert_that(created.customer_id).is_equal_to(customer)

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).is_equal_to(reverse("projects:list"))
