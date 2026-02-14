from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from audit.models import AuditEvent
from experiments.models import Experiment
from projects.models import Project


class AuditTrailTest(TestCase):

    def setUp(self):
        self.project = Project.objects.create(
            name="Test Project",
            description="Test description",
            status="ACTIVE",
            start_date="2024-01-01"
        )

    def test_experiment_create_triggers_audit(self):
        exp = Experiment.objects.create(
            name="Exp1",
            description="Initial",
            status="CREATED",
            data_file="file.csv",
            version="1.0",
            project_id=self.project.id
        )

        audit = AuditEvent.objects.first()

        self.assertIsNotNone(audit)
        self.assertEqual(audit.action, "create")

        expected_ct = ContentType.objects.get_for_model(Experiment)
        self.assertEqual(audit.object_type, expected_ct)

        self.assertIsNotNone(audit.object_id)

    def test_experiment_update_triggers_audit(self):
        exp = Experiment.objects.create(
            name="Exp1",
            description="Initial",
            status="CREATED",
            data_file="file.csv",
            version="1.0",
            project_id=self.project.id
        )

        exp.description = "Updated"
        exp.save()

        self.assertTrue(
            AuditEvent.objects.filter(action="update").exists()
        )

    def test_status_change_triggers_separate_audit(self):
        exp = Experiment.objects.create(
            name="Exp1",
            description="Initial",
            status="CREATED",
            data_file="file.csv",
            version="1.0",
            project_id=self.project.id
        )

        exp.status = "COMPLETED"
        exp.save()

        self.assertTrue(
            AuditEvent.objects.filter(action="status_change").exists()
        )
