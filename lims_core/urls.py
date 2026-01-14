from django.urls import path

from lims_core import views

app_name = "lims_core"

urlpatterns = [
    path("", views.home, name="home"),
]
