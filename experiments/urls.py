from django.urls import path

from . import views

app_name = "experiments"

urlpatterns = [
    path("", views.experiment_list, name="list"),
    path("table/", views.experiment_table, name="table"),
    path("<int:pk>/", views.experiment_detail_tab, name="detail"),  # <-- используем experiment_detail_tab
    path("<int:pk>/tab/", views.experiment_detail_tab, name="detail_tab"),  # <-- для HTMX
    path("<int:pk>/toggle_active/", views.toggle_active, name="toggle_active"),
]
