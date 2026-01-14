"""Tests for the accounts app."""

from assertpy import assert_that

from accounts.models import User


class TestUserModel:
    """Tests for the custom User model."""

    def test_create_user(self, db):
        """User can be created with basic fields."""
        user = User.objects.create_user(
            username="newuser",
            email="new@example.com",
            password="password123",
        )

        assert_that(user.username).is_equal_to("newuser")
        assert_that(user.email).is_equal_to("new@example.com")
        assert_that(user.check_password("password123")).is_true()

    def test_user_sso_fields_default_empty(self, db):
        """SSO-related fields default to empty strings."""
        user = User.objects.create_user(username="ssouser", password="pass")

        assert_that(user.external_id).is_equal_to("")
        assert_that(user.employee_id).is_equal_to("")
        assert_that(user.department).is_equal_to("")

    def test_user_with_sso_fields(self, db):
        """User can be created with SSO fields populated."""
        user = User.objects.create_user(
            username="ssouser",
            password="pass",
            external_id="abc-123-guid",
            employee_id="EMP001",
            department="Chemistry",
        )

        assert_that(user.external_id).is_equal_to("abc-123-guid")
        assert_that(user.employee_id).is_equal_to("EMP001")
        assert_that(user.department).is_equal_to("Chemistry")


class TestUserDisplayName:
    """Tests for the User.display_name() method."""

    def test_display_name_with_full_name(self, db):
        """Returns full name when first and last name are set."""
        user = User.objects.create_user(
            username="jdoe",
            password="pass",
            first_name="John",
            last_name="Doe",
        )

        assert_that(user.display_name()).is_equal_to("John Doe")

    def test_display_name_with_first_name_only(self, db):
        """Returns first name when only first name is set."""
        user = User.objects.create_user(
            username="jane",
            password="pass",
            first_name="Jane",
        )

        assert_that(user.display_name()).is_equal_to("Jane")

    def test_display_name_falls_back_to_email(self, db):
        """Returns email when no name is set."""
        user = User.objects.create_user(
            username="noname",
            email="fallback@example.com",
            password="pass",
        )

        assert_that(user.display_name()).is_equal_to("fallback@example.com")

    def test_display_name_falls_back_to_username(self, db):
        """Returns username when no name or email is set."""
        user = User.objects.create_user(
            username="onlyusername",
            password="pass",
        )

        assert_that(user.display_name()).is_equal_to("onlyusername")

    def test_display_name_strips_whitespace(self, db):
        """Handles names with extra whitespace."""
        user = User.objects.create_user(
            username="spacey",
            password="pass",
            first_name="  ",
            last_name="  ",
            email="spacey@example.com",
        )

        assert_that(user.display_name()).is_equal_to("spacey@example.com")
