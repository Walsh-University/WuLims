from django.urls import path

from lims_core import views

app_name = "lims_core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("search/", views.search, name="search"),

    path("api/status", views.status_public, name="status_public"),
    path("api/status/internal", views.status_internal, name="status_internal"),
]
