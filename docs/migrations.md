# Migrations

This guide explains how Django migrations work and how to manage database schema changes.

## What Are Migrations?

Migrations are Django's way of propagating model changes to the database. When you modify a model (add a field, change a field type, etc.), you create a migration file that describes the change, then apply it to update the database.

```
Model change → makemigrations → Migration file → migrate → Database updated
```

**Why migrations?**
- Track database schema changes in version control
- Apply changes consistently across all environments
- Roll back changes if needed
- Share schema changes with team members

---

## Basic Migration Commands

### Create Migrations

After changing a model, create migration files:

```bash
python manage.py makemigrations
```

This scans all apps for model changes and creates migration files in each app's `migrations/` folder.

**Create migrations for a specific app:**
```bash
python manage.py makemigrations samples
```

### Apply Migrations

Apply pending migrations to the database:

```bash
python manage.py migrate
```

**Apply migrations for a specific app:**
```bash
python manage.py migrate samples
```

### View Migration Status

See which migrations have been applied:

```bash
python manage.py showmigrations
```

Output:
```
accounts
 [X] 0001_initial
 [X] 0002_add_department
samples
 [X] 0001_initial
 [ ] 0002_add_notes  ← Not applied yet
```

### View Migration SQL

See the SQL that a migration will execute:

```bash
python manage.py sqlmigrate samples 0002
```

---

## Step-by-Step: Making a Model Change

### Example: Adding a Field

Let's add a `priority` field to the Sample model.

**1. Modify the model:**

```python
# samples/models.py
class Sample(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        NORMAL = "NORMAL", "Normal"
        HIGH = "HIGH", "High"
        URGENT = "URGENT", "Urgent"

    sample_id = models.CharField(max_length=50, unique=True)
    client_name = models.CharField(max_length=200)
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL  # Default for existing rows
    )
    # ... other fields
```

**2. Create the migration:**

```bash
python manage.py makemigrations samples
```

Output:
```
Migrations for 'samples':
  samples/migrations/0002_sample_priority.py
    - Add field priority to sample
```

**3. Review the migration file:**

```python
# samples/migrations/0002_sample_priority.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('samples', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='priority',
            field=models.CharField(
                choices=[('LOW', 'Low'), ('NORMAL', 'Normal'), ('HIGH', 'High'), ('URGENT', 'Urgent')],
                default='NORMAL',
                max_length=10
            ),
        ),
    ]
```

**4. Apply the migration:**

```bash
python manage.py migrate samples
```

Output:
```
Operations to perform:
  Apply all migrations: samples
Running migrations:
  Applying samples.0002_sample_priority... OK
```

---

## Common Model Changes

### Adding a Required Field

If you add a field without a default, Django will ask what to do with existing rows:

```python
# Adding a required field
description = models.TextField()
```

When you run `makemigrations`:
```
You are trying to add a non-nullable field 'description' to sample.
Please select a fix:
 1) Provide a one-off default now
 2) Quit and add a default in models.py
Select an option:
```

**Best practice:** Always provide a default or make the field nullable:

```python
# Option 1: With default
description = models.TextField(default="")

# Option 2: Nullable
description = models.TextField(null=True, blank=True)
```

### Renaming a Field

```python
# Before
client_name = models.CharField(max_length=200)

# After
customer_name = models.CharField(max_length=200)
```

When you run `makemigrations`, Django will ask:
```
Did you rename sample.client_name to sample.customer_name (a CharField)? [y/N]
```

Answer `y` to rename (preserves data) or `N` to delete and create (loses data).

### Changing Field Type

Be careful when changing field types. Some changes are safe:
- `CharField` max_length increase
- `IntegerField` to `BigIntegerField`

Some require data migration:
- `CharField` to `IntegerField`
- `TextField` to `CharField`

### Adding a ForeignKey

```python
# Add relationship to User
assigned_to = models.ForeignKey(
    "accounts.User",
    on_delete=models.SET_NULL,
    null=True,
    blank=True
)
```

### Removing a Field

Simply delete the field from the model and run `makemigrations`. The data will be permanently deleted.

---

## Migration Files Explained

Migration files are Python code in `app/migrations/`:

```
samples/
└── migrations/
    ├── __init__.py
    ├── 0001_initial.py
    ├── 0002_sample_priority.py
    └── 0003_sample_notes.py
```

**File naming:** `NNNN_description.py`
- `NNNN` - Sequential number
- `description` - Auto-generated or custom name

### Migration Structure

```python
from django.db import migrations, models

class Migration(migrations.Migration):
    # Which migrations must be applied first
    dependencies = [
        ('samples', '0001_initial'),
        ('accounts', '0001_initial'),  # Cross-app dependency
    ]

    # Operations to perform
    operations = [
        migrations.AddField(...),
        migrations.RemoveField(...),
        migrations.AlterField(...),
        migrations.CreateModel(...),
        migrations.DeleteModel(...),
    ]
```

---

## Data Migrations

Sometimes you need to migrate data, not just schema. Use `RunPython`:

```python
from django.db import migrations

def set_default_priority(apps, schema_editor):
    Sample = apps.get_model('samples', 'Sample')
    Sample.objects.filter(priority='').update(priority='NORMAL')

def reverse_priority(apps, schema_editor):
    pass  # Nothing to reverse

class Migration(migrations.Migration):
    dependencies = [
        ('samples', '0002_sample_priority'),
    ]

    operations = [
        migrations.RunPython(set_default_priority, reverse_priority),
    ]
```

**Create an empty migration for data:**
```bash
python manage.py makemigrations samples --empty --name populate_priorities
```

---

## Working with Teams

### Pulling Changes

When you pull code that includes new migrations:

```bash
git pull
python manage.py migrate
```

### Merge Conflicts

If two developers create migrations with the same number:

```
0002_alice_changes.py
0002_bob_changes.py
```

**Solution 1:** Rename one file and update dependencies:
```python
# 0003_bob_changes.py
dependencies = [
    ('samples', '0002_alice_changes'),
]
```

**Solution 2:** Use `--merge` to create a merge migration:
```bash
python manage.py makemigrations --merge samples
```

### Best Practices

1. **Always commit migrations** with your model changes
2. **Run `makemigrations` before committing** to ensure migration exists
3. **Review migration files** before applying
4. **Never edit applied migrations** - create new ones instead
5. **Keep migrations small** - one logical change per migration

---

## Troubleshooting

### "No changes detected"

If `makemigrations` says no changes:

1. Check the app is in `INSTALLED_APPS`
2. Check for syntax errors in models.py
3. Try specifying the app: `python manage.py makemigrations appname`

### "Table already exists"

If you get this error when applying migrations:

```bash
# Fake the migration (mark as applied without running)
python manage.py migrate appname --fake
```

### "Column does not exist"

Your database is out of sync. Try:

```bash
python manage.py migrate --run-syncdb
```

### Reset Migrations (Development Only)

**Warning:** This deletes all data. Only use in development.

```bash
# Delete migration files (keep __init__.py)
rm samples/migrations/0*.py

# Delete database
rm db.sqlite3

# Recreate
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### View Applied Migrations

Check the `django_migrations` table:

```bash
python manage.py shell
>>> from django.db import connection
>>> cursor = connection.cursor()
>>> cursor.execute("SELECT app, name FROM django_migrations ORDER BY id")
>>> cursor.fetchall()
```

---

## Migration Commands Reference

| Command | Purpose |
|---------|---------|
| `makemigrations` | Create migration files from model changes |
| `migrate` | Apply pending migrations |
| `showmigrations` | List all migrations and their status |
| `sqlmigrate app NNNN` | Show SQL for a migration |
| `migrate app NNNN` | Migrate to a specific migration |
| `migrate app zero` | Unapply all migrations for an app |
| `makemigrations --empty` | Create empty migration for data migrations |
| `makemigrations --merge` | Create merge migration for conflicts |
| `migrate --fake` | Mark migration as applied without running |
| `migrate --plan` | Show migration plan without applying |

---

## Example Workflow

### Adding a New Feature with Model Changes

```bash
# 1. Create your feature branch
git checkout -b feature/sample-notes

# 2. Modify models.py
# (add SampleNote model)

# 3. Create migrations
python manage.py makemigrations samples

# 4. Review the migration file
cat samples/migrations/0002_samplenote.py

# 5. Apply migrations locally
python manage.py migrate

# 6. Test your changes
python manage.py runserver

# 7. Commit everything
git add .
git commit -m "Add sample notes feature"

# 8. Push for review
git push -u origin feature/sample-notes
```

---

## Next Steps

- Practice by adding a field to an existing model
- Look at existing migrations in `samples/migrations/` for examples
- Read Django's [migration documentation](https://docs.djangoproject.com/en/5.0/topics/migrations/) for advanced topics
