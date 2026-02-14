from unittest.mock import patch

from assertpy import assert_that

from experiments.models import Experiment


class TestExperimentSignals:
    @patch("experiments.signals.log_audit_event")
    @patch("experiments.signals.get_current_user")
    def test_create_triggers_audit(self, mock_user, mock_log, db, project):
        mock_user.return_value = None

        Experiment.objects.create(
            name="Test",
            description="desc",
            data_file="file",
            version="1.0",
            project=project,
        )

        assert_that(mock_log.called).is_true()

    @patch("experiments.signals.log_audit_event")
    @patch("experiments.signals.get_current_user")
    def test_update_triggers_update_audit(self, mock_user, mock_log, db, project):
        mock_user.return_value = None

        experiment = Experiment.objects.create(
            name="Test",
            description="desc",
            data_file="file",
            version="1.0",
            project=project,
        )

        mock_log.reset_mock()

        experiment.name = "New Name"
        experiment.save()

        assert_that(mock_log.called).is_true()

    @patch("experiments.signals.log_audit_event")
    @patch("experiments.signals.get_current_user")
    def test_status_change_triggers_status_audit(self, mock_user, mock_log, db, project):
        mock_user.return_value = None

        experiment = Experiment.objects.create(
            name="Test",
            description="desc",
            data_file="file",
            version="1.0",
            project=project,
        )

        mock_log.reset_mock()

        experiment.status = "COMPLETED"
        experiment.save()

        assert_that(mock_log.called).is_true()
