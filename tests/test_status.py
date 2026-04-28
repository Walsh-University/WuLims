from unittest.mock import MagicMock, patch

import pytest
from django.db.utils import OperationalError

from lims_core.status import check_database, get_system_status


@pytest.mark.django_db
def test_check_database_success():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)

    mock_connection = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    with patch("lims_core.status.connections") as mock_connections:
        mock_connections.__getitem__.return_value = mock_connection

        result = check_database()

    assert result["name"] == "database"
    assert result["ok"] is True


@pytest.mark.django_db
def test_check_database_failure():
    with patch("lims_core.status.connections") as mock_connections:
        mock_connections.__getitem__.side_effect = OperationalError("DB down")

        result = check_database()

    assert result["name"] == "database"
    assert result["ok"] is False
    assert "detail" in result


def test_get_system_status_operational():
    with patch("lims_core.status.check_database") as mock_check:
        mock_check.return_value = {"name": "database", "ok": True}

        status = get_system_status()

    assert status["status"] == "Operational"
    assert "last_checked" in status
    assert "dependencies" not in status


def test_get_system_status_down():
    with patch("lims_core.status.check_database") as mock_check:
        mock_check.return_value = {"name": "database", "ok": False}

        status = get_system_status()

    assert status["status"] == "Down"


def test_get_system_status_with_internal_dependencies():
    with patch("lims_core.status.check_database") as mock_check:
        mock_check.return_value = {"name": "database", "ok": True}

        status = get_system_status(include_internal=True)

    assert status["status"] == "Operational"
    assert "dependencies" in status
    assert status["dependencies"][0]["name"] == "database"
