from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from audit.models import AuditEvent
from experiments.models import Experiment
from projects.models import Project
from results.models import Result
from samples.models import Sample

User = get_user_model()


class AuditTrailTest(TestCase):
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

    # ===================== Experiments =====================
    def test_experiment_create_triggers_audit(self):
        exp = Experiment.objects.create(
            name="Exp1",
            description="Initial experiment",
            status="CREATED",
            data_file="file.csv",
            version="1.0",
            project=self.project,
        )

        audit = AuditEvent.objects.filter(
            object_type=ContentType.objects.get_for_model(Experiment),
            object_id=exp.id,
            action="create",
        ).first()

        self.assertIsNotNone(audit)
        self.assertIsNone(audit.changes)

    def test_experiment_update_triggers_audit(self):
        exp = Experiment.objects.create(
            name="Exp1",
            description="Initial experiment",
            status="CREATED",
            data_file="file.csv",
            version="1.0",
            project=self.project,
        )

        exp.name = "Updated Name"
        exp.description = "Updated description"
        exp.save()

        audit = AuditEvent.objects.filter(
            object_type=ContentType.objects.get_for_model(Experiment),
            object_id=exp.id,
            action="update",
        ).first()

        self.assertIsNotNone(audit)
        self.assertIn("name", audit.changes)
        self.assertIn("description", audit.changes)
        self.assertEqual(audit.changes["name"]["from"], "Exp1")
        self.assertEqual(audit.changes["name"]["to"], "Updated Name")

    def test_experiment_delete_triggers_audit(self):
        exp = Experiment.objects.create(
            name="Exp1",
            description="Initial experiment",
            status="CREATED",
            data_file="file.csv",
            version="1.0",
            project=self.project,
        )

        exp_id = exp.id
        exp.delete()

        audit = AuditEvent.objects.filter(
            object_type=ContentType.objects.get_for_model(Experiment),
            object_id=exp_id,
            action="delete",
        ).first()

        self.assertIsNotNone(audit)
        self.assertIsNone(audit.changes)

    # ===================== Results =====================
    def test_result_create_triggers_audit(self):
        res = Result.objects.create(
            title="Result1",
            description="Initial result",
            status="ACQUIRED",
            sample=self.sample,
            project=self.project,
        )

        audit = AuditEvent.objects.filter(
            object_type=ContentType.objects.get_for_model(Result),
            object_id=res.id,
            action="create",
        ).first()

        self.assertIsNotNone(audit)
        self.assertIsNone(audit.changes)

    def test_result_update_triggers_audit(self):
        res = Result.objects.create(
            title="Result1",
            description="Initial result",
            status="ACQUIRED",
            sample=self.sample,
            project=self.project,
        )

        res.description = "Updated result"
        res.status = "IN_PROGRESS"
        res.save()

        audit = AuditEvent.objects.filter(
            object_type=ContentType.objects.get_for_model(Result),
            object_id=res.id,
            action="update",
        ).first()

        self.assertIsNotNone(audit)
        self.assertIn("description", audit.changes)
        self.assertIn("status", audit.changes)
        self.assertEqual(audit.changes["description"]["from"], "Initial result")
        self.assertEqual(audit.changes["description"]["to"], "Updated result")
        self.assertEqual(audit.changes["status"]["from"], "ACQUIRED")
        self.assertEqual(audit.changes["status"]["to"], "IN_PROGRESS")

    def test_result_delete_triggers_audit(self):
        res = Result.objects.create(
            title="Result1",
            description="Initial result",
            status="ACQUIRED",
            sample=self.sample,
            project=self.project,
        )

        res_id = res.id
        res.delete()

        audit = AuditEvent.objects.filter(
            object_type=ContentType.objects.get_for_model(Result),
            object_id=res_id,
            action="delete",
        ).first()

        self.assertIsNotNone(audit)
        self.assertIsNone(audit.changes)
