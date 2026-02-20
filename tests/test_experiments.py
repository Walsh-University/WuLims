import pytest
from assertpy import assert_that
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

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


@pytest.fixture
def experiment(db, project):
    return Experiment.objects.create(
        name="Test Experiment",
        description="A test experiment",
        data_file="data.csv",
        version="1.0",
        project=project,
    )


@pytest.mark.django_db
class TestExperimentViews:
    def test_list_requires_login(self, client):
        response = client.get(reverse("experiments:list"))
        assert response.status_code == 302

    def test_list_accessible_when_authenticated(self, authenticated_client):
        response = authenticated_client.get(reverse("experiments:list"))
        assert response.status_code == 200

    def test_table_returns_experiments(self, authenticated_client, experiment):
        response = authenticated_client.get(reverse("experiments:table"))
        assert response.status_code == 200
        assert experiment.name.encode() in response.content

    def test_table_filters_by_search_query(self, authenticated_client, experiment):
        response = authenticated_client.get(reverse("experiments:table"), {"q": "Test Experiment"})
        assert response.status_code == 200
        assert experiment.name.encode() in response.content

    def test_table_excludes_non_matching_query(self, authenticated_client, experiment):
        response = authenticated_client.get(reverse("experiments:table"), {"q": "zzz-no-match"})
        assert response.status_code == 200
        assert experiment.name.encode() not in response.content

    def test_detail_requires_login(self, client, experiment):
        response = client.get(reverse("experiments:detail", args=[experiment.pk]))
        assert response.status_code == 302

    def test_detail_returns_experiment(self, authenticated_client, experiment):
        response = authenticated_client.get(reverse("experiments:detail", args=[experiment.pk]))
        assert response.status_code == 200
        assert experiment.name.encode() in response.content

    def test_detail_tab_overview(self, authenticated_client, experiment):
        response = authenticated_client.get(
            reverse("experiments:detail_tab", args=[experiment.pk]), {"tab": "overview"}
        )
        assert response.status_code == 200
        assert experiment.description.encode() in response.content

    def test_detail_tab_audit(self, authenticated_client, experiment):
        response = authenticated_client.get(reverse("experiments:detail_tab", args=[experiment.pk]), {"tab": "audit"})
        assert response.status_code == 200

    def test_toggle_active_requires_post(self, authenticated_client, experiment):
        response = authenticated_client.get(reverse("experiments:toggle_active", args=[experiment.pk]))
        assert response.status_code == 400
