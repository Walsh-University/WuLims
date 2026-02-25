from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.urls import include, path

from lims_core.status import get_system_status

admin.site.site_header = "WuLims Administration"
admin.site.site_title = "WuLims Admin"
admin.site.index_title = "Operations Console"


def healthz(request):
    return JsonResponse({"status": "ok"}, status=200)


def readyz(request):
    payload = get_system_status(include_internal=True)
    http_status = 200 if payload["status"] == "Operational" else 503
    return JsonResponse(payload, status=http_status)


urlpatterns = [
    path("healthz/", healthz),
    path("readyz/", readyz),
    path("admin/", admin.site.urls),
    # Auth (Django sessions now; later can swap to SSO without changing templates much)
    path("accounts/login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("samples/", include("samples.urls")),
    path("", include("lims_core.urls")),
    path("instruments/", include("instruments.urls")),
    path("results/", include("results.urls")),
    path("experiments/", include("experiments.urls")),
    path("projects/", include("projects.urls")),
    path("customers/", include("customers.urls")),
]

if settings.OIDC_ENABLED:
    urlpatterns.append(path("oidc/", include("mozilla_django_oidc.urls")))
