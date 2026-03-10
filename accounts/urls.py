from django.contrib.auth import views as auth_views
from django.urls import path

from accounts.forms import EmailOrUsernameAuthenticationForm
from accounts.views import CustomerSignupView, VerifyAccountView, WuLimsLoginView

urlpatterns = [
    path(
        "login/",
        WuLimsLoginView.as_view(
            template_name="accounts/login.html",
            authentication_form=EmailOrUsernameAuthenticationForm,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", CustomerSignupView.as_view(), name="signup"),
    path("signup/complete/", CustomerSignupView.as_view(success_page=True), name="signup_complete"),
    path("verify/<uidb64>/<token>/", VerifyAccountView.as_view(), name="verify_account"),
]
