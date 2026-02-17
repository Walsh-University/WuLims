from datetime import date

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase  # ← ИСПРАВЛЕНО

from projects.models import Project
from samples.models import Sample

User = get_user_model()


class AuditTrailTest(TransactionTestCase):  # ← ИСПРАВЛЕНО
    reset_sequences = True  # (рекомендуется для TransactionTestCase)

    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.project = Project.objects.create(
            name="Test Project",
            description="Test description",
            status="ACTIVE",
            start_date=date.today(),
        )
        self.sample = Sample.objects.create(
            sample_name="Test Sample",
            project=self.project,
            client_name="Test Client",
            status="RECEIVED",
        )
