from django.conf import settings


def auth_context(request):
    return {
        "oidc_enabled": getattr(settings, "OIDC_ENABLED", False),
        "oidc_provider_name": getattr(settings, "OIDC_PROVIDER_NAME", "Single Sign-On"),
        "oidc_login_only": getattr(settings, "OIDC_LOGIN_ONLY", False),
    }
