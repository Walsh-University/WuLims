from typing import Any

from django.db import models


def normalize_value(value: Any) -> Any:
    """
    Convert values into JSON-serializable format.
    """

    if isinstance(value, models.Model):
        return str(value.pk)

    if hasattr(value, "isoformat"):  # datetime, date
        return value.isoformat()

    if hasattr(value, "pk"):
        return str(value.pk)

    return value


def compute_diff(
    *,
    old: models.Model,
    new: models.Model,
    fields: list[str],
) -> dict[str, Any] | None:
    """
    Compute field-level diff between two model instances.

    Returns:
    {
        "field_name": {"from": old_value, "to": new_value}
    }
    """

    diff: dict[str, Any] = {}

    for field in fields:
        old_value = getattr(old, field, None)
        new_value = getattr(new, field, None)

        if old_value != new_value:
            diff[field] = {
                "from": normalize_value(old_value),
                "to": normalize_value(new_value),
            }

    return diff or None
