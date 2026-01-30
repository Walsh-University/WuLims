from django.urls import path

from . import views

app_name = "samples"

urlpatterns = [
    path("", views.sample_list, name="list"),
    path("add/", views.sample_add, name="add"),
    path("_table/", views.sample_table, name="table"),
    path("<uuid:pk>/", views.sample_detail, name="detail"),
    path("<uuid:pk>/_approve_modal/", views.approve_modal, name="approve_modal"),
    path("<uuid:pk>/approve/", views.approve_sample, name="approve"),
]
