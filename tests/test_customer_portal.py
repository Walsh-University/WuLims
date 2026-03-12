from assertpy import assert_that
from django.urls import reverse

from customers.models import Customer


class TestCompanyProfileOnboarding:
    def test_customer_contact_without_profile_is_redirected_to_onboarding(self, viewer_client):
        response = viewer_client.get(reverse("customer_portal:home"))

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.headers["Location"]).ends_with(reverse("customer_portal:company_profile"))

    def test_customer_contact_can_create_company_profile(self, viewer_client, viewer_user):
        response = viewer_client.post(
            reverse("customer_portal:company_profile"),
            {
                "customer_name": "Acme Labs",
                "external_id": "ACME-001",
                "customer_type": "Commercial",
            },
        )

        viewer_user.refresh_from_db()
        customer = Customer.objects.get(external_id="ACME-001")
        home_response = viewer_client.get(reverse("customer_portal:home"))
        home_content = home_response.content.decode()

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.headers["Location"]).ends_with(reverse("customer_portal:home"))
        assert_that(viewer_user.customer_profile).is_equal_to(customer)
        assert_that(home_response.status_code).is_equal_to(200)
        assert_that(home_content).contains("Acme Labs")
        assert_that(home_content).contains("ACME-001")
        assert_that(home_content).contains("Commercial")

    def test_duplicate_customer_identifier_shows_user_friendly_error(self, viewer_client):
        Customer.objects.create(
            customer_name="Existing Co",
            external_id="DUPL-001",
            customer_type="University",
        )

        response = viewer_client.post(
            reverse("customer_portal:company_profile"),
            {
                "customer_name": "New Co",
                "external_id": "DUPL-001",
                "customer_type": "Commercial",
            },
        )

        content = response.content.decode()

        assert_that(response.status_code).is_equal_to(200)
        assert_that(content).contains("A company profile with this customer identifier already exists.")

    def test_required_fields_are_validated(self, viewer_client):
        response = viewer_client.post(reverse("customer_portal:company_profile"), {})
        content = response.content.decode()

        assert_that(response.status_code).is_equal_to(200)
        assert_that(content).contains("This field is required.")

    def test_customer_contact_can_update_linked_company_profile(self, viewer_client, viewer_user, customer):
        viewer_user.customer_profile = customer
        viewer_user.save(update_fields=["customer_profile"])

        response = viewer_client.post(
            reverse("customer_portal:company_profile"),
            {
                "customer_name": "Updated Customer",
                "external_id": "123",
                "customer_type": "Research",
            },
        )

        viewer_user.refresh_from_db()
        customer.refresh_from_db()

        assert_that(response.status_code).is_equal_to(302)
        assert_that(viewer_user.customer_profile).is_equal_to(customer)
        assert_that(customer.customer_name).is_equal_to("Updated Customer")
        assert_that(customer.customer_type).is_equal_to("Research")

    def test_non_customer_user_is_redirected_away_from_company_profile_form(self, authenticated_client):
        response = authenticated_client.get(reverse("customer_portal:company_profile"))

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.headers["Location"]).ends_with(reverse("customer_portal:home"))

    def test_non_customer_user_cannot_create_company_profile(self, authenticated_client):
        response = authenticated_client.post(
            reverse("customer_portal:company_profile"),
            {
                "customer_name": "Internal User Co",
                "external_id": "INTERNAL-001",
                "customer_type": "Internal",
            },
        )

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.headers["Location"]).ends_with(reverse("customer_portal:home"))
        assert_that(Customer.objects.filter(external_id="INTERNAL-001").exists()).is_false()

    def test_non_customer_home_does_not_show_company_profile_actions(self, authenticated_client):
        response = authenticated_client.get(reverse("customer_portal:home"))
        content = response.content.decode()

        assert_that(response.status_code).is_equal_to(200)
        assert_that(content).contains("Next step")
        assert_that(content).does_not_contain("Create company profile")
        assert_that(content).does_not_contain("Edit company profile")
