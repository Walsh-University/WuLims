from django.urls import path

from customer_portal import views

app_name = "customer_portal"

urlpatterns = [
    path("", views.home, name="home"),
    path("company-profile/", views.company_profile, name="company_profile"),
    path("contact-profile/", views.contact_profile, name="contact_profile"),
    path("project-request/new/", views.project_request_create, name="project_request_create"),
    path(
        "project-request/<uuid:request_id>/confirmation/",
        views.project_request_confirmation,
        name="project_request_confirmation",
    ),
    path("project-requests/", views.project_request_list, name="project_request_list"),
    path("projects/", views.project_list, name="project_list"),
    path("projects/<int:pk>/", views.project_detail, name="project_detail"),
]
