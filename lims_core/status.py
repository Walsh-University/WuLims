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

    # Overall status rules: database down → Down, any other dep down → Degraded
    check_by_name = {c["name"]: c["ok"] for c in checks}
    if not check_by_name.get("database", False):
        status = "Down"
    elif not all(check_by_name.values()):
        status = "Degraded"
    else:
        status = "Operational"

    payload: dict[str, str | list[dict[str, object]]] = {
        "status": status,
        "last_checked": datetime.now(UTC).isoformat(),
    }

    if include_internal:
        payload["dependencies"] = checks

    return payload
