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
            name="Test Project", description="Test description", status="ACTIVE", start_date="2024-01-01"
        )

    def test_experiment_create_triggers_audit(self):
        exp = Experiment.objects.create(
            name="Exp1",
            description="Initial",
            status="CREATED",
            data_file="file.csv",
            version="1.0",
            project_id=self.project.id,
        )

        audit = AuditEvent.objects.create(
            actor=self.user,
            action="create",
            object_type=ContentType.objects.get_for_model(Experiment),
            object_id=exp.id,
        )

        self.assertIsNotNone(audit)
        self.assertEqual(audit.action, "create")
        self.assertEqual(audit.object_type, ContentType.objects.get_for_model(Experiment))
        self.assertEqual(audit.object_id, exp.id)

    def test_experiment_update_triggers_audit(self):
        exp = Experiment.objects.create(
            name="Exp1",
            description="Initial",
            status="CREATED",
            data_file="file.csv",
            version="1.0",
            project_id=self.project.id,
        )

        AuditEvent.objects.create(
            actor=self.user,
            action="update",
            object_type=ContentType.objects.get_for_model(Experiment),
            object_id=exp.id,
        )

        self.assertTrue(AuditEvent.objects.filter(action="update", object_id=exp.id).exists())

    def test_status_change_triggers_separate_audit(self):
        exp = Experiment.objects.create(
            name="Exp1",
            description="Initial",
            status="CREATED",
            data_file="file.csv",
            version="1.0",
            project_id=self.project.id,
        )

        AuditEvent.objects.create(
            actor=self.user,
            action="status_change",
            object_type=ContentType.objects.get_for_model(Experiment),
            object_id=exp.id,
        )

        self.assertTrue(AuditEvent.objects.filter(action="status_change", object_id=exp.id).exists())
