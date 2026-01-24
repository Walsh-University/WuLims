import os
from pathlib import Path
from urllib.parse import urlparse

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
        # local apps
        "accounts",
        "lims_core",
        "samples",
]

MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
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
                        ],
                },
        },
]

# ---------------------------------------------------------------------
# Database (PostgreSQL)
# ---------------------------------------------------------------------
DATABASES = {
        "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": os.environ.get("DB_NAME", "wulims"),
                "USER": os.environ.get("DB_USER", "wulims"),
                "PASSWORD": os.environ.get("DB_PASSWORD", "wulims_dev_password"),
                "HOST": os.environ.get("DB_HOST", "localhost"),
                "PORT": os.environ.get("DB_PORT", "5432"),
        }
}

# ---------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
        {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "samples:list"
LOGOUT_REDIRECT_URL = "login"

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
    STORAGES = {
            "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"}
    }
else:
    STORAGES = {
            "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------
# Reverse proxy / Traefik (important for CSRF/cookies behind HTTPS)
# ---------------------------------------------------------------------
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Secure cookies in prod; relaxed in dev.py
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
