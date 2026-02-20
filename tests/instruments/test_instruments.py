import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from instruments.models import Instrument

User = get_user_model()


# --------------------------
# Fixtures
# --------------------------
@pytest.fixture
def authenticated_client(client, db):
    """Client with an authenticated user."""
    User.objects.create_user(username="testuser", password="password")
    client.login(username="testuser", password="password")
    return client


@pytest.fixture
def instrument(db):
    """Simple instrument with required fields."""
    return Instrument.objects.create(
        name="TestInstrument",
        serial_number="12345",
        manufacturer="Acme",
        model="X1",
        is_active=True,
    )


# --------------------------
# Instrument Views Tests
# --------------------------
@pytest.mark.django_db
class TestInstrumentViews:
    def test_list_requires_login(self, client):
        url = reverse("instruments:list")
        response = client.get(url)
        assert response.status_code == 302  # redirect to login

    def test_list_accessible_when_authenticated(self, authenticated_client):
        url = reverse("instruments:list")
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_detail_requires_login(self, client, instrument):
        url = reverse("instruments:detail", args=[instrument.pk])
        response = client.get(url)
        assert response.status_code == 302

    def test_detail_returns_instrument(self, authenticated_client, instrument):
        url = reverse("instruments:detail", args=[instrument.pk])
        response = authenticated_client.get(url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "TestInstrument" in content

    def test_toggle_active_requires_login(self, client, instrument):
        url = reverse("instruments:toggle_active", args=[instrument.pk])
        response = client.post(url)
        assert response.status_code == 302

    def test_toggle_active_switches_status(self, authenticated_client, instrument):
        assert instrument.pk is not None

        url = reverse("instruments:toggle_active", args=[instrument.pk])
        response = authenticated_client.post(url)

        instrument.refresh_from_db()
        assert instrument.is_active is False
        assert response.status_code == 200

        content = response.content.decode()
        assert f"instrument-row-{instrument.pk}" in content

    def test_toggle_active_rejects_get(self, authenticated_client, instrument):
        url = reverse("instruments:toggle_active", args=[instrument.pk])
        response = authenticated_client.get(url)
        assert response.status_code == 400

    def test_table_filters_by_name_query(self, authenticated_client, instrument):
        url = reverse("instruments:table")
        response = authenticated_client.get(url, {"q": instrument.name})
        assert response.status_code == 200
        assert instrument.name.encode() in response.content

    def test_table_excludes_non_matching_query(self, authenticated_client, instrument):
        url = reverse("instruments:table")
        response = authenticated_client.get(url, {"q": "zzz-no-match"})
        assert response.status_code == 200
        assert instrument.name.encode() not in response.content

    def test_table_filters_by_manufacturer(self, authenticated_client, instrument):
        url = reverse("instruments:table")
        response = authenticated_client.get(url, {"manufacturer": instrument.manufacturer})
        assert response.status_code == 200
        assert instrument.name.encode() in response.content

    def test_detail_tab_overview(self, authenticated_client, instrument):
        url = reverse("instruments:detail", args=[instrument.pk])
        response = authenticated_client.get(url, {"tab": "overview"})
        assert response.status_code == 200
        assert instrument.manufacturer.encode() in response.content

    def test_detail_tab_maintenance(self, authenticated_client, instrument):
        url = reverse("instruments:detail", args=[instrument.pk])
        response = authenticated_client.get(url, {"tab": "maintenance"})
        assert response.status_code == 200
