"""Tests for the experiments app."""

from assertpy import assert_that

from experiments.models import Experiment


class TestExperimentsModel:
    """Tests for the experiments model."""

    def test_create_experiment(self, db, project):
        """Experiment can be created with required fields."""
        experiment = Experiment.objects.create(
            name="Test",
            description="description",
            status="CREATED",
            data_file="file path",
            version="1.0",
            project_id=project,
        )
        assert_that(experiment.name).is_equal_to("Test")
        assert_that(experiment.description).is_equal_to("description")
        assert_that(experiment.status).is_equal_to("CREATED")
        assert_that(experiment.data_file).is_equal_to("file path")
        assert_that(experiment.version).is_equal_to("1.0")
        assert_that(experiment.project_id).is_equal_to(project)

    def test_experiment_default_values(self, db, project):
        """Experiment creates expected default values."""
        experiment = Experiment.objects.create(
            name="Test", description="description", data_file="file path", version="1.0", project_id=project
        )
        assert_that(experiment.status).is_equal_to("CREATED")
        assert_that(experiment.created_at).is_not_none()

    def test_experiment_cascade_delete(self, db, project):
        """Experiment cascade deletes when project is deleted."""
        experiment = Experiment.objects.create(
            name="Test",
            description="description",
            data_file="file path",
            version="1.0",
            project_id=project,
        )

        assert_that(experiment).is_not_none()
        assert_that(Experiment.objects.count()).is_equal_to(1)
        project.delete()
        assert_that(Experiment.objects.count()).is_equal_to(0)
