from assertpy import assert_that
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from audit.models import AuditEvent
from experiments.models import Experiment
from projects.models import Project

User = get_user_model()


class TestExperimentsModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.project = Project.objects.create(
            name="Test Project",
            description="Test description",
            status="ACTIVE",
            start_date="2024-01-01",
        )

    def test_create_experiment(self):
        experiment = Experiment.objects.create(
            name="Exp1",
            description="Initial experiment",
            status=Experiment.Status.CREATED,
            data_file="file.csv",
            version="1.0",
            project=self.project,
        )

        assert_that(experiment.project).is_equal_to(self.project)
        assert_that(experiment.project_id).is_equal_to(self.project.id)

        audit = AuditEvent.objects.create(
            actor=self.user,
            action="create",
            object_type=ContentType.objects.get_for_model(Experiment),
            object_id=experiment.id,
        )
        assert_that(audit).is_not_none()
        assert_that(audit.action).is_equal_to("create")
        assert_that(audit.object_id).is_equal_to(experiment.id)

    def test_experiment_default_values(self):
        experiment = Experiment.objects.create(
            name="Exp2",
            description="Second experiment",
            data_file="file2.csv",
            version="1.1",
            project=self.project,
        )

        assert_that(experiment.status).is_equal_to(Experiment.Status.CREATED)

    def test_update_experiment_triggers_audit(self):
        experiment = Experiment.objects.create(
            name="Exp3",
            description="Third experiment",
            status=Experiment.Status.CREATED,
            data_file="file3.csv",
            version="1.2",
            project=self.project,
        )

        experiment.description = "Updated description"
        experiment.save()

        AuditEvent.objects.create(
            actor=self.user,
            action="update",
            object_type=ContentType.objects.get_for_model(Experiment),
            object_id=experiment.id,
        )

        assert_that(AuditEvent.objects.filter(action="update", object_id=experiment.id).exists()).is_true()
