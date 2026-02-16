import os

from django.core.wsgi import get_wsgi_application

from config.observability import configure_opentelemetry

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.getenv("DJANGO_SETTINGS_MODULE", "config.settings.prod"),
)

configure_opentelemetry()

application = get_wsgi_application()
