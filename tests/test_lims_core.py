"""Tests for lims_core views."""

from unittest.mock import patch

import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestDashboardView:
    def test_dashboard_requires_login(self, client):
        response = client.get(reverse("lims_core:dashboard"))
        assert response.status_code == 302
        assert "login" in response.url

    def test_dashboard_renders_for_authenticated_user(self, authenticated_client):
        response = authenticated_client.get(reverse("lims_core:dashboard"))
        assert response.status_code == 200


@pytest.mark.django_db
class TestSearchView:
    def test_search_accessible_without_login(self, client):
        response = client.get(reverse("lims_core:search"))
        assert response.status_code == 200

    def test_search_passes_query_to_template(self, client):
        response = client.get(reverse("lims_core:search"), {"q": "metals"})
        assert response.status_code == 200
        assert b"metals" in response.content


@pytest.mark.django_db
class TestStatusPublicView:
    def test_status_public_requires_login(self, client):
        response = client.get(reverse("lims_core:status_public"))
        assert response.status_code == 302

    def test_status_public_returns_json(self, authenticated_client):
        response = authenticated_client.get(reverse("lims_core:status_public"))
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "dependencies" not in data


@pytest.mark.django_db
class TestStatusInternalView:
    def test_status_internal_requires_login(self, client):
        response = client.get(reverse("lims_core:status_internal"))
        assert response.status_code == 302

    def test_status_internal_forbidden_for_non_staff(self, authenticated_client):
        response = authenticated_client.get(reverse("lims_core:status_internal"))
        assert response.status_code == 403

    def test_status_internal_returns_dependencies_for_staff(self, client, admin_user):
        client.force_login(admin_user)
        with patch("lims_core.status.check_database") as mock_check:
            mock_check.return_value = {"name": "database", "ok": True}
            response = client.get(reverse("lims_core:status_internal"))

        assert response.status_code == 200
        data = response.json()
        assert "dependencies" in data
        assert data["status"] == "Operational"
