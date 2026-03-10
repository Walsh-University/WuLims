from django.urls import path

from customer_portal import views

app_name = "customer_portal"

urlpatterns = [
    path("", views.home, name="home"),
]
