"""Shared pytest fixtures for WuLims tests."""

import pytest
from django.test import Client

from accounts.models import User
from samples.models import Sample


@pytest.fixture
def user(db) -> User:
    """Create a basic test user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


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
def sample(db) -> Sample:
    """Create a basic sample in RECEIVED status."""
    return Sample.objects.create(
        sample_id="TEST-001",
        client_name="Test Client",
        status=Sample.Status.RECEIVED,
    )


@pytest.fixture
def sample_in_review(db) -> Sample:
    """Create a sample in IN_REVIEW status (ready for approval)."""
    return Sample.objects.create(
        sample_id="TEST-002",
        client_name="Test Client",
        status=Sample.Status.IN_REVIEW,
    )


@pytest.fixture
def approved_sample(db, user: User) -> Sample:
    """Create an already-approved sample."""
    from django.utils import timezone

    return Sample.objects.create(
        sample_id="TEST-003",
        client_name="Test Client",
        status=Sample.Status.APPROVED,
        approved_at=timezone.now(),
        approved_by=user,
    )
