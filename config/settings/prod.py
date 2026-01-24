from .base import *  # noqa

DEBUG = False

if SECRET_KEY in {"dev-only-change-me"}:  # noqa
    raise RuntimeError("DJANGO_SECRET_KEY must be set in production")
