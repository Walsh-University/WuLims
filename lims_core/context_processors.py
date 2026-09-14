from django.conf import settings


def auth_context(request):
    return {
        "saml_enabled": getattr(settings, "SAML_ENABLED", False),
        "saml_provider_name": getattr(settings, "SAML_PROVIDER_NAME", "Single Sign-On"),
        "saml_login_only": getattr(settings, "SAML_LOGIN_ONLY", False),
    }
