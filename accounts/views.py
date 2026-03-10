from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import FormView

from accounts.forms import PublicCustomerSignupForm
from accounts.models import User

CUSTOMER_CONTACT_GROUP = "Customer Contact"


def is_customer_contact(user) -> bool:
    return user.groups.filter(name=CUSTOMER_CONTACT_GROUP).exists() and not user.is_staff and not user.is_superuser


class WuLimsLoginView(LoginView):
    def get_success_url(self):
        if self.get_redirect_url():
            return self.get_redirect_url()
        if is_customer_contact(self.request.user):
            return reverse("customer_portal:home")
        return super().get_success_url()


class CustomerSignupView(FormView):
    form_class = PublicCustomerSignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("signup_complete")
    success_page = False

    def __init__(self, *args, success_page: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.success_page = success_page

    def dispatch(self, request, *args, **kwargs):
        if self.success_page:
            return render(request, "accounts/signup_complete.html")
        if request.user.is_authenticated:
            return redirect(
                "customer_portal:home" if is_customer_contact(request.user) else settings.LOGIN_REDIRECT_URL
            )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        group, _ = Group.objects.get_or_create(name=CUSTOMER_CONTACT_GROUP)
        user.groups.add(group)
        self._send_verification_email(user)
        return super().form_valid(form)

    def _send_verification_email(self, user: User) -> None:
        uid = urlsafe_base64_encode(str(user.pk).encode())
        token = default_token_generator.make_token(user)
        verification_url = self.request.build_absolute_uri(reverse("verify_account", args=[uid, token]))
        subject = "Verify your WuLims account"
        body = render_to_string(
            "accounts/emails/verify_account.txt",
            {
                "user": user,
                "verification_url": verification_url,
            },
        )
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])


class VerifyAccountView(View):
    template_name = "accounts/verification_result.html"

    def get(self, request, uidb64: str, token: str):
        user = self._get_user(uidb64)
        if user is None or not default_token_generator.check_token(user, token):
            return render(
                request,
                self.template_name,
                {
                    "title": "Verification link invalid",
                    "message": "This verification link is invalid or has expired.",
                },
                status=400,
            )

        user.is_active = True
        user.save(update_fields=["is_active"])
        login(request, user)
        return render(
            request,
            self.template_name,
            {
                "title": "Account verified",
                "message": "Your account has been verified. You can now access the customer portal.",
                "cta_label": "Open customer portal",
                "cta_url": reverse("customer_portal:home"),
            },
        )

    @staticmethod
    def _get_user(uidb64: str):
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            return User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None
