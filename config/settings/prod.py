from .base import *  # noqa

DEBUG = False

if SECRET_KEY in {"dev-only-change-me", "dev-only-change-me"}:
    raise RuntimeError("DJANGO_SECRET_KEY must be set in production")
