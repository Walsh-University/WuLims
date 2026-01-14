from django.urls import path
from . import views

app_name = "samples"

urlpatterns = [
    path("", views.sample_list, name="list"),
    path("_table/", views.sample_table, name="table"),
    path("<int:pk>/", views.sample_detail, name="detail"),

    path("<int:pk>/_approve_modal/", views.approve_modal, name="approve_modal"),
    path("<int:pk>/approve/", views.approve_sample, name="approve"),
]
