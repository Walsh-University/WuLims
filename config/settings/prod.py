from .base import *  # noqa
import os

DEBUG = False

if SECRET_KEY == "dev-only-change-me":  # noqa # pragma: allowlist secret
    raise RuntimeError("DJANGO_SECRET_KEY must be set in production")

# Hosts (Traefik + kube probes)
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split()
ALLOWED_HOSTS = [h for h in ALLOWED_HOSTS if h]  # drop empties
DJANGO_ALLOWED_HOSTS = ALLOWED_HOSTS  # for base.py usage

# CSRF
CSRF_TRUSTED_ORIGINS = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split()
CSRF_TRUSTED_ORIGINS = [o for o in CSRF_TRUSTED_ORIGINS if o]

# Traefik does TLS termination:
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
