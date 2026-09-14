"""Tests for the WuLims SAML2 authentication backend."""

import pytest

from accounts.models import User
from accounts.saml import WuLimsSaml2Backend, _clean_username

ATTRIBUTE_MAPPING = {
    "http://schemas.microsoft.com/identity/claims/objectidentifier": ("external_id",),
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress": ("email",),
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname": ("first_name",),
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname": ("last_name",),
    "employeeid": ("employee_id",),
    "department": ("department",),
}


def make_attributes(**overrides) -> dict:
    values = {
        "http://schemas.microsoft.com/identity/claims/objectidentifier": "oid-abc-123",
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress": "newuser@example.com",
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname": "New",
        "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname": "User",
        "employeeid": "EMP001",
        "department": "Lab",
    }
    values.update(overrides)
    return {key: [value] for key, value in values.items() if value is not None}


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
    return WuLimsSaml2Backend()


# --- get_or_create_user ---


@pytest.mark.django_db
def test_lookup_by_external_id_matches_existing_user(backend, user):
    user.external_id = "oid-abc-123"
    user.save(update_fields=["external_id"])

    found, created = backend.get_or_create_user(
        "external_id",
        "oid-abc-123",
        True,
        idp_entityid="https://sts.windows.net/tenant/",
        attributes=make_attributes(),
        attribute_mapping=ATTRIBUTE_MAPPING,
        request=None,
    )
    assert found == user
    assert created is False


@pytest.mark.django_db
def test_falls_back_to_email_when_no_external_id_match(backend, user):
    found, created = backend.get_or_create_user(
        "external_id",
        "oid-does-not-exist",
        True,
        idp_entityid="https://sts.windows.net/tenant/",
        attributes=make_attributes(
            **{"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress": user.email}
        ),
        attribute_mapping=ATTRIBUTE_MAPPING,
        request=None,
    )
    assert found == user
    assert created is False


@pytest.mark.django_db
def test_email_fallback_backfills_blank_external_id(backend, user):
    assert user.external_id == ""

    found, created = backend.get_or_create_user(
        "external_id",
        "oid-newly-seen",
        True,
        idp_entityid="https://sts.windows.net/tenant/",
        attributes=make_attributes(
            **{"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress": user.email}
        ),
        attribute_mapping=ATTRIBUTE_MAPPING,
        request=None,
    )
    found.refresh_from_db()
    assert created is False
    assert found.external_id == "oid-newly-seen"


@pytest.mark.django_db
def test_creates_user_when_no_match_found(backend):
    created_user, created = backend.get_or_create_user(
        "external_id",
        "oid-brand-new",
        True,
        idp_entityid="https://sts.windows.net/tenant/",
        attributes=make_attributes(),
        attribute_mapping=ATTRIBUTE_MAPPING,
        request=None,
    )
    assert created is True
    assert created_user.username == "newuser"
    assert created_user.external_id == "oid-brand-new"
    assert not created_user.has_usable_password()


@pytest.mark.django_db
def test_create_user_handles_username_collision(backend):
    User.objects.create_user(username="newuser", password="x")

    created_user, created = backend.get_or_create_user(
        "external_id",
        "oid-brand-new",
        True,
        idp_entityid="https://sts.windows.net/tenant/",
        attributes=make_attributes(),
        attribute_mapping=ATTRIBUTE_MAPPING,
        request=None,
    )
    assert created is True
    assert created_user.username == "newuser_2"


@pytest.mark.django_db
def test_create_user_falls_back_to_external_id_for_username_when_no_email(backend):
    created_user, created = backend.get_or_create_user(
        "external_id",
        "oid-no-email",
        True,
        idp_entityid="https://sts.windows.net/tenant/",
        attributes=make_attributes(**{"http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress": None}),
        attribute_mapping=ATTRIBUTE_MAPPING,
        request=None,
    )
    assert created is True
    assert created_user.username == "oid-no-email"
    assert created_user.email == ""


@pytest.mark.django_db
def test_returns_none_when_create_unknown_user_disabled(backend):
    found, created = backend.get_or_create_user(
        "external_id",
        "oid-brand-new",
        False,
        idp_entityid="https://sts.windows.net/tenant/",
        attributes=make_attributes(),
        attribute_mapping=ATTRIBUTE_MAPPING,
        request=None,
    )
    assert found is None
    assert created is False
