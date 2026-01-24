from .base import *  # noqa

DEBUG = False

if SECRET_KEY in {"dev-only-change-me"}:  # noqa
    raise RuntimeError("DJANGO_SECRET_KEY must be set in production")

# Traefik does TLS termination:
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
