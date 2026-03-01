import uuid

from django.db import models


class Customer(models.Model):
    class Active(models.TextChoices):
        ACTIVE = "ACTIVE"
        INACTIVE = "INACTIVE"

    customer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_name = models.CharField(max_length=200)
    external_id = models.CharField(max_length=32, unique=True)
    customer_type = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.CharField(max_length=20, choices=Active.choices, default=Active.INACTIVE)

    def __str__(self):
        return self.customer_name


class Person(models.Model):
    class Title(models.TextChoices):
        MR = "MR"
        MS = "MS"
        MRS = "MRS"
        DR = "DR"

    person_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="people")
    title = models.CharField(max_length=10, choices=Title.choices, blank=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    suffix = models.CharField(max_length=50, blank=True)
    job_title = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class CustomerAddress(models.Model):
    class AddressType(models.TextChoices):
        BILLING = "billing", "Billing"
        SHIPPING = "shipping", "Shipping"
        MAILING = "mailing", "Mailing"
        OTHER = "other", "Other"

    address_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="addresses")
    address_type = models.CharField(max_length=20, choices=AddressType.choices)
    address_line_one = models.CharField(max_length=200)
    address_line_two = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["customer_id"],
                condition=models.Q(is_primary=True),
                name="customers_one_primary_address_per_customer",
            )
        ]

    def __str__(self):
        return f"{self.address_line_one}, {self.city}"


class PersonPhoneNumber(models.Model):
    class PhoneType(models.TextChoices):
        OFFICE = "office", "Office"
        CELL = "cell", "Cell"
        PERSONAL = "personal", "Personal"
        FAX = "fax", "Fax"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person_id = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="phone_numbers",
    )
    phone_number = models.CharField(max_length=32)
    phone_type = models.CharField(max_length=20, choices=PhoneType.choices)
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["person_id"],
                condition=models.Q(is_primary=True),
                name="customers_one_primary_phone_per_person",
            )
        ]

    def __str__(self):
        return f"{self.phone_number} ({self.phone_type})"


class PersonEmail(models.Model):
    person_id = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="email_addresses")
    email = models.EmailField()
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["person_id", "email"], name="uniq_person_email"),
            models.UniqueConstraint(
                fields=["person_id"], condition=models.Q(is_primary=True), name="uniq_primary_email_per_person"
            ),
        ]

    def __str__(self):
        return self.email
