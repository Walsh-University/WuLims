import re
from typing import Any

from django.contrib.auth import get_user_model
from mozilla_django_oidc.auth import OIDCAuthenticationBackend


def _clean_username(raw: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]", "_", raw).strip("._-")
    return cleaned[:150] or "user"


class WuLimsOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def _base_username_from_claims(self, claims: dict[str, Any]) -> str:
        preferred = claims.get("preferred_username")
        if preferred:
            return _clean_username(str(preferred).split("@")[0])

        email = claims.get("email")
        if email:
            return _clean_username(str(email).split("@")[0])

        subject = claims.get("sub")
        if subject:
            return _clean_username(str(subject))

        return "user"

    def _unique_username(self, base: str):
        User = get_user_model()
        candidate = base
        suffix = 1
        while User.objects.filter(username=candidate).exists():
            suffix += 1
            candidate = f"{base}_{suffix}"[:150]
        return candidate

    def _claim(self, claims: dict[str, Any], *keys: str, default: str = "") -> str:
        for key in keys:
            value = claims.get(key)
            if value:
                return str(value)
        return default

    def filter_users_by_claims(self, claims: dict[str, Any]):
        User = get_user_model()

        subject = self._claim(claims, "sub")
        if subject:
            users = User.objects.filter(external_id=subject)
            if users.exists():
                return users

        email = self._claim(claims, "email", "upn")
        if email:
            return User.objects.filter(email__iexact=email)

        return User.objects.none()

    def create_user(self, claims: dict[str, Any]):
        User = get_user_model()

        base_username = self._base_username_from_claims(claims)
        username = self._unique_username(base_username)

        user = User.objects.create(
            username=username,
            email=self._claim(claims, "email", "upn"),
            first_name=self._claim(claims, "given_name"),
            last_name=self._claim(claims, "family_name"),
            external_id=self._claim(claims, "sub"),
            employee_id=self._claim(claims, "employee_id", "employeeId"),
            department=self._claim(claims, "department"),
            is_active=True,
        )
        user.set_unusable_password()
        user.save(update_fields=["password"])
        return user

    def update_user(self, user, claims: dict[str, Any]):
        updates = []

        subject = self._claim(claims, "sub")
        if subject and user.external_id != subject:
            user.external_id = subject
            updates.append("external_id")

        email = self._claim(claims, "email", "upn")
        if email and user.email != email:
            user.email = email
            updates.append("email")

        first_name = self._claim(claims, "given_name")
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            updates.append("first_name")

        last_name = self._claim(claims, "family_name")
        if last_name and user.last_name != last_name:
            user.last_name = last_name
            updates.append("last_name")

        employee_id = self._claim(claims, "employee_id", "employeeId")
        if employee_id and user.employee_id != employee_id:
            user.employee_id = employee_id
            updates.append("employee_id")

        department = self._claim(claims, "department")
        if department and user.department != department:
            user.department = department
            updates.append("department")

        if updates:
            user.save(update_fields=updates)

        return user
