import os

from django.core.asgi import get_asgi_application

from config.observability import configure_opentelemetry

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.getenv("DJANGO_SETTINGS_MODULE", "config.settings.prod"),
)

configure_opentelemetry()

application = get_asgi_application()
