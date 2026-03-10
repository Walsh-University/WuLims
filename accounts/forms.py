from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Email or username", max_length=254)

    error_messages = {
        **AuthenticationForm.error_messages,
        "inactive": "This account is not verified yet. Check your email for the verification link.",
    }

    def clean(self):
        identifier = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if identifier and password:
            resolved_user = self._resolve_user(identifier)
            if resolved_user and not resolved_user.is_active:
                raise ValidationError(
                    self.error_messages["inactive"],
                    code="inactive",
                )

            username = resolved_user.username if resolved_user else identifier
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password,
            )

            if self.user_cache is None:
                raise self.get_invalid_login_error()

            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    @staticmethod
    def _resolve_user(identifier: str):
        email_matches = list(User.objects.filter(email__iexact=identifier)[:2])
        if len(email_matches) == 1:
            return email_matches[0]
        return User.objects.filter(username__iexact=identifier).first()


class PublicCustomerSignupForm(UserCreationForm):
    email = forms.EmailField(label="Email")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"]
        user.email = email
        user.username = email
        user.is_active = False

        if commit:
            user.save()

        return user
