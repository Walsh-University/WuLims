from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from audit.models import AuditEvent
from experiments.models import Experiment
from projects.models import Project

User = get_user_model()


class AuditTrailTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.project = Project.objects.create(
            name="Test Project",
            description="Test description",
            status="ACTIVE",
            start_date="2024-01-01",
        )

    def test_experiment_create_triggers_audit(self):
        exp = Experiment.objects.create(
            name="Exp1",
            description="Initial",
            status="CREATED",
            data_file="file.csv",
            version="1.0",
            project=self.project,
        )

        # Проверяем, что сигнал создал AuditEvent
        audit = AuditEvent.objects.filter(
            object_type=ContentType.objects.get_for_model(Experiment),
            object_id=exp.id,
            action="create",
        ).first()

        self.assertIsNotNone(audit)

    def test_experiment_update_triggers_audit(self):
        exp = Experiment.objects.create(
            name="Exp1",
            description="Initial",
            status="CREATED",
            data_file="file.csv",
            version="1.0",
            project=self.project,
        )

        exp.name = "Updated Name"
        exp.save()

        self.assertTrue(
            AuditEvent.objects.filter(
                object_type=ContentType.objects.get_for_model(Experiment),
                object_id=exp.id,
                action="update",
            ).exists()
        )

    def test_status_change_triggers_separate_audit(self):
        exp = Experiment.objects.create(
            name="Exp1",
            description="Initial",
            status="CREATED",
            data_file="file.csv",
            version="1.0",
            project=self.project,
        )

        exp.status = "RUNNING"
        exp.save()

        self.assertTrue(
            AuditEvent.objects.filter(
                object_type=ContentType.objects.get_for_model(Experiment),
                object_id=exp.id,
                action="update",
            ).exists()
        )
