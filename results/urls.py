from django.urls import path

from . import views

app_name = "results"

urlpatterns = [
    path("", views.results_list, name="list"),
    path("<int:pk>/", views.result_detail, name="detail"),
    path("_table/", views.results_table, name="table"),
    path("<int:pk>/edit/", views.results_list, name="edit"),
    path("<int:pk>/_approve_modal/", views.approve_modal, name="approve_modal"),
    path("add/", views.result_add, name="add"),
]
