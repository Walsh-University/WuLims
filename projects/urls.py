from django.urls import path

from . import views
from .views import project_request_create, project_request_success

app_name = "projects"

urlpatterns = [
    path("", views.project_list, name="list"),
    path("add/", views.project_add, name="add"),
    path("_table/", views.project_table, name="table"),
    path("request/new/", project_request_create, name="project_request_create"),
    path("request/success/<int:pk>/", project_request_success, name="project_request_success"),
]
