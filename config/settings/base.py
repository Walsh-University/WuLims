import os
from pathlib import Path
from urllib.parse import urlparse

import dj_database_url

from config.observability import build_logging_config, configure_structlog

# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------
# base.py is config/settings/base.py, so project root is 3 levels up
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def env_bool(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [x.strip() for x in raw.split(",") if x.strip()]


# ---------------------------------------------------------------------
# Core settings
# ---------------------------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-change-me")
DEBUG = env_bool("DJANGO_DEBUG", "0")

DJANGO_PUBLIC_URL = os.getenv("DJANGO_PUBLIC_URL", "")

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", "")

# If a public URL is provided, ensure its host/origin is trusted
if DJANGO_PUBLIC_URL:
    u = urlparse(DJANGO_PUBLIC_URL)
    if u.hostname and u.hostname not in ALLOWED_HOSTS and "*" not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(u.hostname)
    if u.scheme and u.netloc:
        origin = f"{u.scheme}://{u.netloc}"
        if origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(origin)


LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "INFO").upper()
JSON_LOGS = env_bool("DJANGO_JSON_LOGS", "1")
configure_structlog()
LOGGING = build_logging_config(log_level=LOG_LEVEL, json_logs=JSON_LOGS)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "no-reply@wulims.local")

# ---------------------------------------------------------------------
# Apps / middleware
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_structlog",
    "djangosaml2",
    # local apps
    "accounts",
    "experiments.apps.ExperimentsConfig",
    "lims_core",
    "projects",
    "samples",
    "instruments",
    "audit",
    "customers.apps.CustomersConfig",
    "results.apps.ResultsConfig",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "audit.middleware.RequestIDMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_structlog.middlewares.RequestMiddleware",
    "accounts.audit.RoleAuditActorMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "audit.middleware.AuditUserMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "lims_core.context_processors.auth_context",
            ],
        },
    },
]

# ---------------------------------------------------------------------
# Database (PostgreSQL)
# ---------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=int(os.getenv("DB_CONN_MAX_AGE", "600")),
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "wulims"),
            "USER": os.environ.get("DB_USER", "wulims"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "wulims_dev_password"),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
            "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
        }
    }

# ---------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

SAML_ENABLED = env_bool("SAML_ENABLED", "0")
SAML_PROVIDER_NAME = os.getenv("SAML_PROVIDER_NAME", "Microsoft Entra")
SAML_LOGIN_ONLY = env_bool("SAML_LOGIN_ONLY", "0")

SAML_SP_ENTITY_ID = os.getenv("SAML_SP_ENTITY_ID", "")
SAML_ACS_URL = os.getenv("SAML_ACS_URL", "")
SAML_IDP_METADATA_FILE = os.getenv("SAML_IDP_METADATA_FILE", "")
SAML_SP_KEY_FILE = os.getenv("SAML_SP_KEY_FILE", "")
SAML_SP_CERT_FILE = os.getenv("SAML_SP_CERT_FILE", "")
SAML_XMLSEC_BINARY = os.getenv("SAML_XMLSEC_BINARY", "/usr/bin/xmlsec1")

# djangosaml2: which User field identifies a SAML user, and which SAML
# attribute (via SAML_ATTRIBUTE_MAPPING below) supplies its value.
SAML_DJANGO_USER_MAIN_ATTRIBUTE = "external_id"
SAML_CREATE_UNKNOWN_USER = True

# Maps Entra's default SAML claim URIs (plus the custom "employeeid"/
# "department" claims configured on the Enterprise App) to User fields.
SAML_ATTRIBUTE_MAPPING = {
    "http://schemas.microsoft.com/identity/claims/objectidentifier": ("external_id",),
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress": ("email",),
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname": ("first_name",),
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname": ("last_name",),
    "employeeid": ("employee_id",),
    "department": ("department",),
}

if SAML_ENABLED:
    import saml2

    SAML_CONFIG = {
        "xmlsec_binary": SAML_XMLSEC_BINARY,
        "entityid": SAML_SP_ENTITY_ID,
        "allow_unknown_attributes": True,
        "service": {
            "sp": {
                "endpoints": {
                    "assertion_consumer_service": [
                        (SAML_ACS_URL, saml2.BINDING_HTTP_POST),
                    ],
                },
                "allow_unsolicited": True,
                "authn_requests_signed": True,
                "want_response_signed": True,
            },
        },
        "metadata": {
            "local": [SAML_IDP_METADATA_FILE] if SAML_IDP_METADATA_FILE else [],
        },
        "key_file": SAML_SP_KEY_FILE,
        "cert_file": SAML_SP_CERT_FILE,
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "samples:list"
LOGOUT_REDIRECT_URL = "login"

if SAML_ENABLED:
    AUTHENTICATION_BACKENDS.insert(0, "accounts.saml.WuLimsSaml2Backend")

# ---------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "America/New_York")
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------
# Static files / WhiteNoise
# ---------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# WhiteNoise storage backend
if DEBUG:
    STORAGES = {"staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"}}
else:
    STORAGES = {"staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------
# Reverse proxy / Traefik (important for CSRF/cookies behind HTTPS)
# ---------------------------------------------------------------------
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Secure cookies in prod; relaxed in dev.py
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
