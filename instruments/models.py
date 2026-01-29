from django.conf import settings

from django.db import models


class Instrument(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    model = models.CharField(max_length=200, blank=True)
    serial_number = models.CharField(max_length=100, blank=True, unique=True)
    is_active = models.BooleanField(default=True)
    last_calibration_date = models.DateField(null=True, blank=True)
    last_maintenance_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="instruments_created"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="instruments_updated"
    )

    def __str__(self):
        return self.name
