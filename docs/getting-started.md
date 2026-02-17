# Getting Started

This guide covers environment setup and Django fundamentals for new developers.

## Prerequisites

- Python 3.13 or higher
- Git
- A code editor
  - PyCharm (recommended)
  - VS Code (also good)
- Zed (lightweight)
  - Any IDE that supports Python and Django
- Docker

## Docker vs Local Dev (Quick Note)

You can run WuLims in two ways:

- **Local dev**: Use `uv`, run `python manage.py runserver`, and connect to PostgreSQL.
- **Docker**: Run the app in a container with Gunicorn, automatic migrations, and static file collection. This is closer to production and avoids local dependency drift.

Most students should start with **local dev** for easier debugging, then try Docker once the basics feel comfortable.

## Environment Setup

### 1. Install uv (Package Manager)

We use `uv` instead of pip. It's faster and handles virtual environments better.

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and Set Up the Project

```bash
# Clone the repository
git clone git@github.com:Walsh-University/WuLims.git
cd WuLims

# Create a virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
uv sync
```

### 3. Database Setup (PostgreSQL)

WuLims uses PostgreSQL for local runtime. The simplest path is to run Postgres via Docker:

```bash
# Start PostgreSQL
docker compose -f docker/docker-compose.yml up -d db

# Optional: set env vars explicitly (defaults already match these values)
export DB_NAME=wulims
export DB_USER=wulims
export DB_PASSWORD=wulims_dev_password
export DB_HOST=localhost
export DB_PORT=5432
```

Alternatively, copy `.env.example` to `.env` and source it:

```bash
cp .env.example .env
source .env  # or use a tool like direnv
```

Do not commit `.env` to version control. It contains local configuration values and secrets.

To stop PostgreSQL later:
```bash
docker compose -f docker/docker-compose.yml down        # Stop container (keeps data)
docker compose -f docker/docker-compose.yml down -v     # Stop and delete all data
```

### 4. Initialize the Database

```bash
# Create database tables
python manage.py migrate

# Create an admin account
python manage.py createsuperuser
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ in your browser.

---

## Django Fundamentals

Django follows the **MTV pattern** (Model-Template-View), which is similar to MVC:

| Django | Traditional MVC | Purpose |
|--------|-----------------|---------|
| Model | Model | Database structure and business logic |
| Template | View | HTML presentation |
| View | Controller | Request handling and response |

### The Request-Response Cycle

```
Browser Request
      ↓
   urls.py (URL routing)
      ↓
   views.py (Process request)
      ↓
   models.py (Database queries)
      ↓
   template.html (Render HTML)
      ↓
Browser Response
```

### Key Django Concepts

#### Models (`models.py`)

Models define your database structure. Each model becomes a database table.

```python
from django.db import models

class Sample(models.Model):
    sample_id = models.CharField(max_length=50, unique=True)
    client_name = models.CharField(max_length=200)
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sample_id
```

- `CharField` - Text with max length
- `DateTimeField` - Date and time
- `ForeignKey` - Relationship to another model
- `auto_now_add=True` - Automatically set on creation

#### Views (`views.py`)

Views handle HTTP requests and return responses. We use **function-based views**.

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def sample_list(request):
    samples = Sample.objects.all()
    return render(request, "samples/sample_list.html", {"samples": samples})
```

- `@login_required` - User must be logged in
- `request` - Contains HTTP request data
- `render()` - Combines template with context data

#### URLs (`urls.py`)

URL patterns map URLs to views.

```python
from django.urls import path
from . import views

app_name = "samples"  # Namespace for reverse lookups

urlpatterns = [
    path("", views.sample_list, name="list"),
    path("<int:pk>/", views.sample_detail, name="detail"),
]
```

- `app_name` - Enables namespaced URLs like `samples:list`
- `<int:pk>` - Captures an integer from the URL
- `name="list"` - Name for reverse URL lookups

#### Templates

Templates are HTML files with Django template language.

```html
{% extends "lims_core/base.html" %}

{% block content %}
<h1>Samples</h1>
<ul>
{% for sample in samples %}
    <li>{{ sample.sample_id }} - {{ sample.client_name }}</li>
{% empty %}
    <li>No samples found.</li>
{% endfor %}
</ul>
{% endblock %}
```

- `{% extends %}` - Inherit from a base template
- `{% block %}` - Define/override content blocks
- `{% for %}` - Loop over items
- `{{ variable }}` - Output a variable

---

## Common Commands

```bash
# Run development server
python manage.py runserver

# Create migrations after model changes
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Open Django shell
python manage.py shell

# Run tests with coverage
uv run pytest

# Run linter
uv run ruff check .

# Run type checker
uv run ty check .

# Format code
uv run ruff format .

# Check for Django issues
python manage.py check
```

See [Testing](testing.md) for more details on writing and running tests.

---

## Adding Dependencies

Use `uv` to add new packages:

```bash
# Add a package
uv add package-name

# Add a development-only package
uv add --dev package-name

# Update all packages
uv sync --upgrade
```

Dependencies are stored in `pyproject.toml`.

---

## Development Workflow

1. **Pull latest changes**: `git pull`
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make changes** to models, views, templates
4. **Run migrations** if you changed models
5. **Test locally** with the dev server
6. **Commit changes**: `git add . && git commit -m "Description"`
7. **Push branch**: `git push -u origin feature/your-feature`
8. **Create Pull Request** for review

---

## Troubleshooting

### "No module named 'django'"
Your virtual environment isn't activated. Run:
```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### "Port already in use"
Another process is using port 8000. Use a different port:
```bash
python manage.py runserver 8001
```

### "Migration errors"
If migrations are out of sync:
```bash
python manage.py migrate --run-syncdb
```

### "Permission denied" on macOS
Make sure you have write permissions to the project directory.

---

## Next Steps

- Read [Project Structure](project-structure.md) to understand the codebase layout
- Read [Architecture](architecture.md) to learn about HTMX patterns
- Read [Creating Views](creating-views.md) when you're ready to add features
- Read [Testing](testing.md) to learn how to write and run tests
