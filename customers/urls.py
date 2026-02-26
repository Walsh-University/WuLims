from django.urls import path

from . import views

app_name = "customers"

urlpatterns = [
    path("", views.customer_list, name="list"),
    path("add/", views.customer_add, name="add"),
    path("_table/", views.customer_table, name="table"),
    path("<uuid:pk>/", views.customer_detail, name="detail"),
]
