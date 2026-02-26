# Django Relationships

## ForeignKey

ForeignKey is used to establish a one-to-many relationship between two models. It creates a foreign key column in the model that references the primary key of another model. The related_name attribute specifies the reverse relation from the related model back to this model.

A simple example of a ForeignKey relationship:
```python
from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author,
                               on_delete=models.CASCADE,
                               related_name='books')
```
Books can be accessed from an Author instance using `author_instance.books.all()`.

Authors can write many books, but each book has only one author.

## ManyToManyField
ManyToManyField is used to establish a many-to-many relationship between two models. It creates an intermediary table that holds references to both models.

A simple example of a ManyToManyField relationship:

```python
from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)

class Course(models.Model):
    title = models.CharField(max_length=100)
    students = models.ManyToManyField(Student,
                                      related_name='courses')
```

Courses can be accessed from a Student instance using `student_instance.courses.all()`.

Students can enroll in many courses, and each course can have many students.

## OneToOneField

OneToOneField is used to establish a one-to-one relationship between two models. It creates a unique constraint on the foreign key column, ensuring that each instance of the model can be related to only one instance of the other model.

A simple example of a OneToOneField relationship:

```python
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField('auth.User',
                                on_delete=models.CASCADE,
                                related_name='profile')
    bio = models.TextField()
```
UserProfile can be accessed from a User instance using `user_instance.profile`.

Each user has one profile, and each profile is associated with one user.

These relationship fields are essential for modeling complex data structures in Django applications. They allow for efficient querying and data manipulation across related models.

## WuLims Example

```python
class Person(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="people"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class PersonEmail(models.Model):
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="email_addresses"
    )
    email = models.EmailField()
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["person", "email"], name="uniq_person_email"),
            models.UniqueConstraint(
                fields=["person"],
                condition=models.Q(is_primary=True),
                name="uniq_primary_email_per_person",
            ),
        ]

    def __str__(self):
        return self.email

```

In this example, a `Person` is related to a `Customer` via a ForeignKey, indicating that each customer can have
multiple people associated with them. The `PersonEmail` model also uses a ForeignKey to relate email addresses
to a specific person, allowing each person to have multiple email addresses.

## Understanding `related_name`

The `related_name` attribute allows reverse access to related objects, such as accessing all people associated with a customer using `customer_instance.people.all()` and all email addresses associated with a person using `person_instance.email_addresses.all()`.

Without `related_name`, Django would use default names like `person_set` and `personemail_set`, which can be less intuitive.

**Without** `related_name`:
```python
person.personemail_set.all()
```

**With** `related_name`:
```python
person.email_addresses.all()
```

`related_name` is how you want to talk about the relationship in English.

## Understanding `on_delete`

`on_delete=models.CASCADE` tells Django to delete all related `Person` or `PersonEmail` records if the associated `Customer` or `Person` is deleted.

This helps maintain data integrity by ensuring that there are no orphaned records in the database.

For example, if a `Customer` is deleted, all associated `Person` records will also be deleted. Similarly, if a `Person` is deleted, all associated `PersonEmail` records will be deleted.

Most common options for `on_delete` include:
- `CASCADE` → delete children automatically
- `PROTECT` → prevent deletion if children exist
- `SET_NULL` → keep child, null FK (requires null=True)
- `RESTRICT` → newer, stricter PROTECT

Example `on_delete` usage:

| Relationship | `on_delete` behavior |
|---|---|
| Customer → Project | `PROTECT` |
| Experiment → Sample | `PROTECT` |
| Person → Email | `CASCADE` |
| Person → Phone | `CASCADE` |


## Updating Existing Models

When adding a new relationship field to an existing model, you may need to provide a default value for existing records. This can be done by specifying a default value in the migration file or by allowing null values temporarily.

For example, if you add a ForeignKey field to an existing model, you can set a default value in the migration:

Example adding ForeignKey with default in migration to the existing Samples model:
```python
experiment = models.ForeignKey(
    Experiment,
    on_delete=models.PROTECT,
    related_name="samples",
    null=True,   # TEMPORARY
)
```
null=True allows existing records to have a null value temporarily. After the migration, you can update the records and then remove null=True in a subsequent migration.

Without null=True, Django will prompt you to provide a default value for existing records during the migration process.

After the migration has been applied to the database, you can run a data migration or use the Django shell to set appropriate values for the new relationship field on existing records. Once all records have valid values, you can create another migration to remove `null=True`.

## Summary

### One-to-many in Django

- ForeignKey lives on the “many” side
- related_name gives reverse access
- on_delete encodes business rules
- Migrations tell the story of the system evolving
