"""Tests for the accounts app."""

from assertpy import assert_that
from django.contrib.auth.models import Group
from django.urls import reverse

from accounts.audit import role_audit_actor
from accounts.models import RoleAssignmentAudit, User
from accounts.roles import ROLE_PERMISSIONS


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


class TestRoleAssignments:
    """Tests for role creation and role audit tracking."""

    def test_baseline_roles_exist(self, db):
        role_names = list(Group.objects.values_list("name", flat=True))

        assert_that(role_names).contains(*ROLE_PERMISSIONS.keys())

    def test_baseline_roles_have_documented_permissions(self, db):
        for role_name, expected_permissions in ROLE_PERMISSIONS.items():
            group = Group.objects.get(name=role_name)
            actual_permissions = {
                f"{permission.content_type.app_label}.{permission.codename}" for permission in group.permissions.all()
            }
            assert_that(actual_permissions).is_equal_to(expected_permissions)

    def test_role_assignment_is_audited(self, db):
        actor = User.objects.create_superuser(username="adminrole", password="pass")
        target = User.objects.create_user(username="staffrole", password="pass")
        role = Group.objects.get(name="Lab Tech")

        with role_audit_actor(actor):
            target.groups.add(role)

        audit = RoleAssignmentAudit.objects.get(user=target, role_name="Lab Tech")
        assert_that(audit.action).is_equal_to(RoleAssignmentAudit.Action.ASSIGNED)
        assert_that(audit.changed_by).is_equal_to(actor)
        assert_that(audit.changed_at).is_not_none()

    def test_role_removal_is_audited(self, db):
        actor = User.objects.create_superuser(username="adminremove", password="pass")
        target = User.objects.create_user(username="staffremove", password="pass")
        role = Group.objects.get(name="Analyst")
        target.groups.add(role)

        with role_audit_actor(actor):
            target.groups.remove(role)

        audit = RoleAssignmentAudit.objects.filter(
            user=target,
            role_name="Analyst",
            action=RoleAssignmentAudit.Action.REMOVED,
        ).latest("changed_at")
        assert_that(audit.changed_by).is_equal_to(actor)


class TestAdminSiteBranding:
    """Tests for admin branding and navigation affordances."""

    def test_admin_index_has_wulims_brand_and_back_link(self, client, admin_user):
        client.force_login(admin_user)

        response = client.get(reverse("admin:index"))
        content = response.content.decode()

        assert_that(response.status_code).is_equal_to(200)
        assert_that(content).contains("WuLims Administration")
        assert_that(content).contains("Back to WuLims App")
        assert_that(content).contains(reverse("lims_core:dashboard"))
