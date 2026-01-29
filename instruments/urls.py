from django.urls import path
from . import views

app_name = "instruments"

urlpatterns = [
    path("", views.instrument_list, name="list"),
    path("table/", views.instrument_table, name="table"),
    path("<int:pk>/", views.instrument_detail, name="detail"),
    path("<int:pk>/toggle_active/", views.toggle_active, name="toggle_active"),
    # path("<int:pk>/edit/", views.edit_modal, name="edit_modal"),  # commented out
]
