import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from instruments.models import Instrument

User = get_user_model()


# --------------------------
# Фикстуры
# --------------------------
@pytest.fixture
def authenticated_client(client, db):
    """Клиент с авторизованным пользователем."""
    user = User.objects.create_user(username="testuser", password="password")
    client.login(username="testuser", password="password")
    return client


@pytest.fixture
def instrument(db):
    """Простой инструмент с обязательными полями."""
    return Instrument.objects.create(
        name="TestInstrument",
        serial_number="12345",
        manufacturer="Acme",
        model="X1",
        is_active=True,
    )


# --------------------------
# Тесты вьюшек Instruments
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
