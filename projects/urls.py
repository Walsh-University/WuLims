from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("", views.project_list, name="list"),
    path("add/", views.project_add, name="add"),
    path("_table/", views.project_table, name="table"),
]
