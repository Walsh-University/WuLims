from datetime import UTC, datetime

from django.db import connections
from django.db.utils import OperationalError


def check_database():
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()
        return {"name": "database", "ok": True}
    except OperationalError as e:
        return {"name": "database", "ok": False, "detail": str(e)}


def get_system_status(include_internal: bool = False):
    checks = [check_database()]

    # Overall status rules
    if not checks[0]["ok"]:
        status = "Down"
    elif any(not c["ok"] for c in checks):
        status = "Degraded"
    else:
        status = "Operational"

    payload = {
        "status": status,
        "last_checked": datetime.now(UTC).isoformat(),
    }

    if include_internal:
        payload["dependencies"] = checks

    return payload
