"""Tests for the customers app."""

import pytest
from assertpy import assert_that
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from customers.models import Person, PersonPhoneNumber, PersonEmail


class TestPeopleModel:
    """Tests for customer contact people."""

    def test_person_belongs_to_customer(self, db, customer):
        """A person belongs to a customer."""
        person = Person.objects.create(
            customer_id=customer,
            first_name="Grace",
            last_name="Hopper",
        )

        assert_that(person.customer_id).is_equal_to(customer)

    def test_person_has_name(self, db, customer):
        """A person must have a first and last name."""
        person = Person(customer_id=customer, first_name="", last_name="")

        with pytest.raises(ValidationError):
            person.full_clean()

    def test_customer_can_have_multiple_people(self, db, customer):
        """A customer can have many people."""
        Person.objects.create(customer_id=customer, first_name="Marie", last_name="Curie")
        Person.objects.create(customer_id=customer, first_name="Rosalind", last_name="Franklin")

        assert_that(customer.people.count()).is_equal_to(2)


class TestPersonPhoneNumberModel:
    """Tests for person phone numbers."""

    def test_phone_number_belongs_to_person(self, db, customer):
        """A phone number belongs to one person."""
        person = Person.objects.create(customer_id=customer, first_name="Grace", last_name="Hopper")
        phone = PersonPhoneNumber.objects.create(
            person_id=person,
            phone_number="330-555-0100",
            phone_type=PersonPhoneNumber.PhoneType.OFFICE,
        )

        assert_that(phone.person_id).is_equal_to(person)

    def test_person_can_have_multiple_phone_numbers(self, db, customer):
        """A person can have multiple phone numbers."""
        person = Person.objects.create(customer_id=customer, first_name="Marie", last_name="Curie")
        PersonPhoneNumber.objects.create(
            person_id=person,
            phone_number="330-555-0101",
            phone_type=PersonPhoneNumber.PhoneType.CELL,
        )
        PersonPhoneNumber.objects.create(
            person_id=person,
            phone_number="330-555-0102",
            phone_type=PersonPhoneNumber.PhoneType.FAX,
        )

        assert_that(person.phone_numbers.count()).is_equal_to(2)

    def test_phone_number_has_type(self, db, customer):
        """Phone numbers store a type from defined choices."""
        phone_types = [choice[0] for choice in PersonPhoneNumber.PhoneType.choices]

        assert_that(phone_types).contains("office", "cell", "fax")

    def test_only_one_primary_phone_per_person(self, db, customer):
        """Only one phone number may be primary for a person."""
        person = Person.objects.create(customer_id=customer, first_name="Ada", last_name="Lovelace")
        PersonPhoneNumber.objects.create(
            person_id=person,
            phone_number="330-555-0103",
            phone_type=PersonPhoneNumber.PhoneType.CELL,
            is_primary=True,
        )

        with pytest.raises(IntegrityError):
            PersonPhoneNumber.objects.create(
                person_id=person,
                phone_number="330-555-0104",
                phone_type=PersonPhoneNumber.PhoneType.OFFICE,
                is_primary=True,
            )


class TestPersonEmailModel:
    """Tests for person email addresses."""

    def test_email_belongs_to_one_person(self, db, customer):
        person = Person.objects.create(customer_id=customer, first_name="Ada", last_name="Lovelace")
        email = PersonEmail.objects.create(person_id=person, email="ada@example.com")

        assert_that(email.person_id).is_equal_to(person)

    def test_person_can_have_multiple_emails(self, db, customer):
        person = Person.objects.create(customer_id=customer, first_name="Niels", last_name="Bohr")
        PersonEmail.objects.create(person_id=person, email="niels.work@example.com")
        PersonEmail.objects.create(person_id=person, email="niels.personal@example.com")

        assert_that(person.email_addresses.count()).is_equal_to(2)

    def test_only_one_primary_email_allowed_per_person(self, db, customer):
        person = Person.objects.create(customer_id=customer, first_name="Chien", last_name="Shiung Wu")
        PersonEmail.objects.create(person_id=person, email="wu.primary@example.com", is_primary=True)

        with pytest.raises(IntegrityError):
            PersonEmail.objects.create(person_id=person, email="wu.alt@example.com", is_primary=True)

    def test_email_must_be_unique_per_person(self, db, customer):
        person = Person.objects.create(customer_id=customer, first_name="Katherine", last_name="Johnson")
        PersonEmail.objects.create(person_id=person, email="kj@example.com")

        with pytest.raises(IntegrityError):
            PersonEmail.objects.create(person_id=person, email="kj@example.com")

    def test_same_email_can_exist_for_different_people(self, db, customer):
        person_one = Person.objects.create(customer_id=customer, first_name="Person", last_name="One")
        person_two = Person.objects.create(customer_id=customer, first_name="Person", last_name="Two")

        PersonEmail.objects.create(person_id=person_one, email="shared@example.com")
        PersonEmail.objects.create(person_id=person_two, email="shared@example.com")

        assert_that(PersonEmail.objects.filter(email="shared@example.com").count()).is_equal_to(2)
