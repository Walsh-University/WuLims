from django.urls import path

from customer_portal import views

app_name = "customer_portal"

urlpatterns = [
    path("", views.home, name="home"),
    path("company-profile/", views.company_profile, name="company_profile"),
    path("contact-profile/", views.contact_profile, name="contact_profile"),
]
