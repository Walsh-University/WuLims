"""Tests for the customers app."""

import pytest
from assertpy import assert_that
from django.core.exceptions import ValidationError

from customers.models import Person


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
