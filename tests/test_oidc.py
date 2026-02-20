"""Tests for the WuLims OIDC authentication backend."""

import pytest

from accounts.models import User
from accounts.oidc import WuLimsOIDCAuthenticationBackend, _clean_username

# --- _clean_username ---


def test_clean_username_replaces_special_chars():
    assert _clean_username("john@example.com") == "john_example.com"


def test_clean_username_strips_leading_dots_and_dashes():
    assert _clean_username(".hidden-user") == "hidden-user"


def test_clean_username_returns_user_for_empty_string():
    assert _clean_username("") == "user"


def test_clean_username_truncates_to_150():
    long = "a" * 200
    assert len(_clean_username(long)) == 150


# --- Backend fixture ---


@pytest.fixture
def backend():
    return WuLimsOIDCAuthenticationBackend()


# --- filter_users_by_claims ---


@pytest.mark.django_db
def test_filter_by_sub_matches_external_id(backend, user):
    user.external_id = "sub-abc-123"
    user.save(update_fields=["external_id"])

    result = backend.filter_users_by_claims({"sub": "sub-abc-123"})
    assert result.first() == user


@pytest.mark.django_db
def test_filter_by_email_when_no_sub_match(backend, user):
    result = backend.filter_users_by_claims({"email": user.email})
    assert result.first() == user


@pytest.mark.django_db
def test_filter_by_upn_fallback(backend, user):
    result = backend.filter_users_by_claims({"upn": user.email})
    assert result.first() == user


@pytest.mark.django_db
def test_filter_returns_empty_when_no_claims_match(backend):
    result = backend.filter_users_by_claims({"sub": "does-not-exist"})
    assert not result.exists()


@pytest.mark.django_db
def test_filter_returns_empty_for_empty_claims(backend):
    result = backend.filter_users_by_claims({})
    assert not result.exists()


# --- create_user ---


@pytest.mark.django_db
def test_create_user_populates_fields(backend):
    claims = {
        "sub": "new-sub-999",
        "email": "newuser@example.com",
        "given_name": "New",
        "family_name": "User",
        "preferred_username": "newuser",
        "employee_id": "EMP001",
        "department": "Lab",
    }
    created = backend.create_user(claims)

    assert created.username == "newuser"
    assert created.email == "newuser@example.com"
    assert created.first_name == "New"
    assert created.last_name == "User"
    assert created.external_id == "new-sub-999"
    assert created.employee_id == "EMP001"
    assert created.department == "Lab"
    assert not created.has_usable_password()


@pytest.mark.django_db
def test_create_user_falls_back_to_email_for_username(backend):
    claims = {
        "sub": "sub-xyz",
        "email": "fallback@example.com",
    }
    created = backend.create_user(claims)
    assert created.username == "fallback"


@pytest.mark.django_db
def test_create_user_handles_username_collision(backend):
    User.objects.create_user(username="collision", password="x")
    claims = {
        "sub": "sub-col",
        "preferred_username": "collision",
        "email": "collision2@example.com",
    }
    created = backend.create_user(claims)
    assert created.username == "collision_2"


# --- update_user ---


@pytest.mark.django_db
def test_update_user_syncs_changed_fields(backend, user):
    claims = {
        "sub": "updated-sub",
        "email": "updated@example.com",
        "given_name": "Updated",
        "family_name": "Name",
        "employee_id": "EMP999",
        "department": "QA",
    }
    updated = backend.update_user(user, claims)
    updated.refresh_from_db()

    assert updated.email == "updated@example.com"
    assert updated.first_name == "Updated"
    assert updated.last_name == "Name"
    assert updated.external_id == "updated-sub"
    assert updated.employee_id == "EMP999"
    assert updated.department == "QA"


@pytest.mark.django_db
def test_update_user_noop_when_claims_unchanged(backend, user):
    original_email = user.email
    updated = backend.update_user(user, {"email": original_email})
    updated.refresh_from_db()

    assert updated.email == original_email


@pytest.mark.django_db
def test_update_user_skips_empty_claim_values(backend, user):
    original_email = user.email
    updated = backend.update_user(user, {"email": ""})
    updated.refresh_from_db()

    assert updated.email == original_email
