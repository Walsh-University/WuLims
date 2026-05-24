from assertpy import assert_that
from django.urls import reverse

from audit.models import AuditEvent
from customers.models import Customer, Person


class TestCompanyProfileOnboarding:
    def test_customer_contact_without_profile_is_redirected_to_onboarding(self, viewer_client):
        response = viewer_client.get(reverse("customer_portal:home"))

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.headers["Location"]).ends_with(reverse("customer_portal:company_profile"))

    def test_customer_contact_with_company_but_no_contact_is_redirected_to_contact_profile(
        self, viewer_client, viewer_user, customer
    ):
        viewer_user.customer_profile = customer
        viewer_user.save(update_fields=["customer_profile"])

        response = viewer_client.get(reverse("customer_portal:home"))

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.headers["Location"]).ends_with(reverse("customer_portal:contact_profile"))

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

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.headers["Location"]).ends_with(reverse("customer_portal:home"))
        assert_that(viewer_user.customer_profile).is_equal_to(customer)

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

    def test_customer_contact_cannot_open_contact_profile_before_company_profile(self, viewer_client):
        response = viewer_client.get(reverse("customer_portal:contact_profile"))

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.headers["Location"]).ends_with(reverse("customer_portal:company_profile"))

    def test_customer_contact_can_create_contact_profile(self, viewer_client, viewer_user, customer):
        viewer_user.customer_profile = customer
        viewer_user.save(update_fields=["customer_profile"])

        response = viewer_client.post(
            reverse("customer_portal:contact_profile"),
            {
                "title": Person.Title.DR,
                "first_name": "Ada",
                "last_name": "Lovelace",
                "job_title": "Laboratory Director",
                "is_active": "on",
            },
        )

        viewer_user.refresh_from_db()
        person = Person.objects.get(pk=viewer_user.contact_profile_id)
        home_response = viewer_client.get(reverse("customer_portal:home"))
        home_content = home_response.content.decode()
        audit = AuditEvent.objects.get(object_id=str(person.pk), action="create")

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.headers["Location"]).ends_with(reverse("customer_portal:home"))
        assert_that(person.customer_id).is_equal_to(customer)
        assert_that(person.first_name).is_equal_to("Ada")
        assert_that(person.last_name).is_equal_to("Lovelace")
        assert_that(person.job_title).is_equal_to("Laboratory Director")
        assert_that(person.is_active).is_true()
        assert_that(viewer_user.contact_profile).is_equal_to(person)
        assert_that(viewer_user.first_name).is_equal_to("Ada")
        assert_that(viewer_user.last_name).is_equal_to("Lovelace")
        assert_that(home_response.status_code).is_equal_to(200)
        assert_that(home_content).contains("Test Customer")
        assert_that(home_content).contains("123")
        assert_that(home_content).contains("Ada Lovelace")
        assert_that(home_content).contains("Laboratory Director")
        assert_that(audit.actor).is_equal_to(viewer_user)

    def test_customer_contact_can_update_contact_profile(self, viewer_client, viewer_user, customer):
        person = Person.objects.create(
            customer_id=customer,
            title=Person.Title.MS,
            first_name="Grace",
            last_name="Hopper",
            job_title="Scientist",
            is_active=True,
        )
        viewer_user.customer_profile = customer
        viewer_user.contact_profile = person
        viewer_user.save(update_fields=["customer_profile", "contact_profile"])

        response = viewer_client.post(
            reverse("customer_portal:contact_profile"),
            {
                "title": Person.Title.DR,
                "first_name": "Grace",
                "last_name": "Hopper",
                "job_title": "Chief Scientist",
                "is_active": "",
            },
        )

        viewer_user.refresh_from_db()
        person.refresh_from_db()
        audit = AuditEvent.objects.get(object_id=str(person.pk), action="update")

        assert_that(response.status_code).is_equal_to(302)
        assert_that(person.customer_id).is_equal_to(customer)
        assert_that(person.title).is_equal_to(Person.Title.DR)
        assert_that(person.job_title).is_equal_to("Chief Scientist")
        assert_that(person.is_active).is_false()
        assert_that(audit.actor).is_equal_to(viewer_user)
        assert_that(audit.changes).contains_key("title", "job_title", "is_active")

    def test_contact_profile_required_fields_are_validated(self, viewer_client, viewer_user, customer):
        viewer_user.customer_profile = customer
        viewer_user.save(update_fields=["customer_profile"])

        response = viewer_client.post(reverse("customer_portal:contact_profile"), {})
        content = response.content.decode()

        assert_that(response.status_code).is_equal_to(200)
        assert_that(content).contains("This field is required.")

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
        assert_that(content).does_not_contain("Create contact profile")
        assert_that(content).does_not_contain("Edit contact profile")


class TestProjectRequestWorkflow:
    def test_customer_contact_can_submit_project_request(self, viewer_client, viewer_user, customer):
       person = Person.objects.create(
           customer_id=customer,
           title=Person.Title.MR,
           first_name="John",
           last_name="Doe",
           job_title="Research Director",
           is_active=True,
       )
       viewer_user.customer_profile = customer
       viewer_user.contact_profile = person
       viewer_user.save(update_fields=["customer_profile", "contact_profile"])

       response = viewer_client.post(
           reverse("customer_portal:project_request_create"),
           {
               "business_context": "We need to analyze sample composition for quality control.",
               "scientific_context": "We require HPLC analysis with mass spectrometry confirmation.",
           },
       )

       assert_that(response.status_code).is_equal_to(302)
       assert_that(response.headers["Location"]).contains("confirmation")

    def test_project_request_confirmation_shows_request_id(self, viewer_client, viewer_user, customer):
       person = Person.objects.create(
           customer_id=customer,
           title=Person.Title.MS,
           first_name="Jane",
           last_name="Smith",
           job_title="Lab Manager",
           is_active=True,
       )
       viewer_user.customer_profile = customer
       viewer_user.contact_profile = person
       viewer_user.save(update_fields=["customer_profile", "contact_profile"])

       response = viewer_client.post(
           reverse("customer_portal:project_request_create"),
           {
               "business_context": "Quality control analysis required.",
               "scientific_context": "Standard HPLC protocol.",
           },
       )

       # Extract request_id from redirect location
       from customer_portal.models import ProjectRequest
       request_obj = ProjectRequest.objects.latest("created_at")

       confirmation_response = viewer_client.get(
           reverse("customer_portal:project_request_confirmation", kwargs={"request_id": request_obj.request_id})
       )
       content = confirmation_response.content.decode()

       assert_that(confirmation_response.status_code).is_equal_to(200)
       assert_that(content).contains(str(request_obj.request_id))
       assert_that(content).contains("Pending")
       assert_that(content).contains("Request Submitted Successfully")

    def test_customer_cannot_access_another_customers_request(self, viewer_client, viewer_user, customer):
       from customer_portal.models import ProjectRequest

       # Create another customer and request
       other_customer = Customer.objects.create(
           customer_name="Other Company",
           external_id="OTHER-123",
           customer_type="Commercial",
       )
       other_person = Person.objects.create(
           customer_id=other_customer,
           title=Person.Title.MR,
           first_name="Bob",
           last_name="Brown",
           job_title="Manager",
           is_active=True,
       )
       other_request = ProjectRequest.objects.create(
           customer=other_customer,
           requesting_contact=other_person,
           business_context="Other company request",
           scientific_context="Other company science",
       )

       # Setup viewer user with first customer
       person = Person.objects.create(
           customer_id=customer,
           title=Person.Title.MR,
           first_name="Alice",
           last_name="Anderson",
           job_title="Analyst",
           is_active=True,
       )
       viewer_user.customer_profile = customer
       viewer_user.contact_profile = person
       viewer_user.save(update_fields=["customer_profile", "contact_profile"])

       # Try to access other customer's request
       response = viewer_client.get(
           reverse("customer_portal:project_request_confirmation", kwargs={"request_id": other_request.request_id})
       )

       assert_that(response.status_code).is_equal_to(404)

    def test_customer_can_list_only_their_project_requests(self, viewer_client, viewer_user, customer):
       from customer_portal.models import ProjectRequest

       # Create another customer with request
       other_customer = Customer.objects.create(
           customer_name="Another Company",
           external_id="ANOTHER-456",
           customer_type="Commercial",
       )
       other_person = Person.objects.create(
           customer_id=other_customer,
           title=Person.Title.MS,
           first_name="Carol",
           last_name="Clark",
           job_title="Director",
           is_active=True,
       )

       # Create requests for both customers
       own_request = ProjectRequest.objects.create(
           customer=customer,
           requesting_contact=viewer_user.contact_profile or Person.objects.create(
               customer_id=customer,
               title=Person.Title.MR,
               first_name="David",
               last_name="Davis",
               job_title="Scientist",
               is_active=True,
           ),
           business_context="My request",
           scientific_context="My science",
       )
       other_request = ProjectRequest.objects.create(
           customer=other_customer,
           requesting_contact=other_person,
           business_context="Other request",
           scientific_context="Other science",
       )

       # Setup viewer user
       if not viewer_user.contact_profile:
           person = own_request.requesting_contact
           viewer_user.contact_profile = person
       viewer_user.customer_profile = customer
       viewer_user.save(update_fields=["customer_profile", "contact_profile"])

       response = viewer_client.get(reverse("customer_portal:project_request_list"))
       content = response.content.decode()

       assert_that(response.status_code).is_equal_to(200)
       assert_that(content).contains(str(own_request.request_id))
       assert_that(content).does_not_contain(str(other_request.request_id))

    def test_non_customer_cannot_create_project_request(self, authenticated_client):
       response = authenticated_client.get(reverse("customer_portal:project_request_create"))

       assert_that(response.status_code).is_equal_to(404)
