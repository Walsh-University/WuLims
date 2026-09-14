import logging
import re
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import MultipleObjectsReturned
from djangosaml2.backends import Saml2Backend

logger = logging.getLogger(__name__)


def _clean_username(raw: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]", "_", raw).strip("._-")
    return cleaned[:150] or "user"


class WuLimsSaml2Backend(Saml2Backend):
    def _unique_username(self, base: str) -> str:
        User = get_user_model()
        candidate = base
        suffix = 1
        while User.objects.filter(username=candidate).exists():
            suffix += 1
            candidate = f"{base}_{suffix}"[:150]
        return candidate

    def get_or_create_user(
        self,
        user_lookup_key: str,
        user_lookup_value: Any,
        create_unknown_user: bool,
        idp_entityid: str,
        attributes: dict,
        attribute_mapping: dict,
        request,
    ):
        User = get_user_model()
        lookup_suffix = getattr(settings, "SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP", "")

        try:
            user = User.objects.get(**{user_lookup_key + lookup_suffix: user_lookup_value})
            return user, False
        except User.DoesNotExist:
            pass
        except MultipleObjectsReturned:
            logger.error("Multiple users matched %s=%s", user_lookup_key, user_lookup_value)
            return None, False

        email = self._get_attribute_value("email", attributes, attribute_mapping)
        if email:
            matches = list(User.objects.filter(email__iexact=email))
            if len(matches) == 1:
                user = matches[0]
                if user_lookup_key == "external_id" and not user.external_id:
                    user.external_id = user_lookup_value
                    user.save(update_fields=["external_id"])
                return user, False

        if not create_unknown_user:
            return None, False

        base_username = _clean_username((email or str(user_lookup_value)).split("@")[0])
        username = self._unique_username(base_username)

        user = User.objects.create(
            username=username,
            email=email or "",
            external_id=user_lookup_value if user_lookup_key == "external_id" else "",
            is_active=True,
        )
        user.set_unusable_password()
        user.save(update_fields=["password"])
        return user, True
