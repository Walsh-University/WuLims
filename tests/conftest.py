"""Shared pytest fixtures for WuLims tests."""

import pytest
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import Client

from accounts.models import User
from accounts.roles import ROLE_PERMISSIONS
from customers.models import Customer
from projects.models import Project
from samples.models import Sample


def ensure_role_permissions(role_name: str) -> Group:
    group, _ = Group.objects.get_or_create(name=role_name)

    permissions = []
    for permission_ref in ROLE_PERMISSIONS[role_name]:
        app_label, codename = permission_ref.split(".")
        model = "sample" if app_label == "samples" else "user"
        content_type = ContentType.objects.get(app_label=app_label, model=model)
        permissions.append(Permission.objects.get(content_type=content_type, codename=codename))

    group.permissions.set(permissions)
    return group


@pytest.fixture
def user(db) -> User:
    """Create a basic test user."""
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )
    lab_tech = ensure_role_permissions("Lab Tech")
    user.groups.add(lab_tech)
    return user


@pytest.fixture
def admin_user(db) -> User:
    """Create an admin/superuser."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
    )


@pytest.fixture
def authenticated_client(client: Client, user: User) -> Client:
    """Return a Django test client logged in as the test user."""
    client.force_login(user)
    return client


@pytest.fixture
def reviewer_user(db) -> User:
    """Create a QA reviewer user with approve permissions via role assignment."""
    user = User.objects.create_user(
        username="reviewer",
        email="reviewer@example.com",
        password="reviewerpass123",
    )
    reviewer_group = ensure_role_permissions("QA Reviewer")
    user.groups.add(reviewer_group)
    return user


@pytest.fixture
def reviewer_client(client: Client, reviewer_user: User) -> Client:
    """Return a test client logged in as a QA reviewer."""
    client.force_login(reviewer_user)
    return client


@pytest.fixture
def manager_user(db) -> User:
    """Create a lab manager user with sample create/update permissions."""
    user = User.objects.create_user(
        username="manager",
        email="manager@example.com",
        password="managerpass123",
    )
    manager_group = ensure_role_permissions("Lab Manager")
    user.groups.add(manager_group)
    return user


@pytest.fixture
def manager_client(client: Client, manager_user: User) -> Client:
    """Return a test client logged in as a lab manager."""
    client.force_login(manager_user)
    return client


@pytest.fixture
def viewer_user(db) -> User:
    """Create a view-only user (Customer Contact role)."""
    user = User.objects.create_user(
        username="viewer",
        email="viewer@example.com",
        password="viewerpass123",
    )
    viewer_group = ensure_role_permissions("Customer Contact")
    user.groups.add(viewer_group)
    return user


@pytest.fixture
def viewer_client(client: Client, viewer_user: User) -> Client:
    """Return a test client logged in as a view-only user."""
    client.force_login(viewer_user)
    return client


@pytest.fixture
def sample(db, project: Project) -> Sample:
    """Create a basic sample in RECEIVED status."""
    return Sample.objects.create(
        project=project,
        client_name="Test Client",
        status=Sample.Status.RECEIVED,
    )


@pytest.fixture
def sample_in_review(db, project: Project) -> Sample:
    """Create a sample in IN_REVIEW status (ready for approval)."""
    return Sample.objects.create(
        project=project,
        client_name="Test Client",
        status=Sample.Status.IN_REVIEW,
    )


@pytest.fixture
def approved_sample(db, user: User, project: Project) -> Sample:
    """Create an already-approved sample."""
    from django.utils import timezone

    return Sample.objects.create(
        project=project,
        client_name="Test Client",
        status=Sample.Status.APPROVED,
        approved_at=timezone.now(),
        approved_by=user,
    )


@pytest.fixture
def project(db) -> Project:
    """Create a basic project."""
    return Project.objects.create(name="Test Project", start_date="2026-01-01")


@pytest.fixture
def customer(db) -> Customer:
    """Create a basic customer."""
    return Customer.objects.create(customer_name="Test Customer", external_id="123", customer_type="Test")
