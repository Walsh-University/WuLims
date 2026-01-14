from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Future-proof fields for AD/SSO
    external_id = models.CharField(max_length=255, blank=True, default="", help_text="SSO subject / GUID")
    employee_id = models.CharField(max_length=64, blank=True, default="")
    department = models.CharField(max_length=128, blank=True, default="")

    def display_name(self) -> str:
        full = self.get_full_name().strip()
        return full if full else (self.email or self.username)
