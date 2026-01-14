# Project Structure

This document explains the directory layout and purpose of each component in WuLims.

## Directory Overview

```
WuLims/
├── config/                 # Django project configuration
├── accounts/               # User authentication app
├── lims_core/              # Core app (base templates, shared components)
├── samples/                # Sample management app
├── static/                 # Static files (CSS, JS, images)
├── docs/                   # Documentation (you are here)
├── manage.py               # Django CLI entry point
├── pyproject.toml          # Dependencies and project metadata
├── uv.lock                 # Locked dependency versions
├── docker-compose.yml      # PostgreSQL container configuration
└── .env.example            # Environment variable template
```

---

## Configuration (`config/`)

The Django project configuration. This is created when you run `django-admin startproject`.

```
config/
├── __init__.py
├── settings.py         # All Django settings
├── urls.py             # Root URL routing
├── wsgi.py             # WSGI entry point (production)
└── asgi.py             # ASGI entry point (async/websockets)
```

### `settings.py`

Key settings to know:

```python
# Custom user model (always use this pattern)
AUTH_USER_MODEL = "accounts.User"

# Installed apps - add new apps here
INSTALLED_APPS = [
    # Django built-ins
    "django.contrib.admin",
    "django.contrib.auth",
    # ...

    # Our apps
    "accounts",
    "lims_core",
    "samples",
]

# Where to redirect after login/logout
LOGIN_REDIRECT_URL = "samples:list"
LOGOUT_REDIRECT_URL = "login"
```

**Database Configuration:**

The database backend is configured via environment variables:
- If `DB_NAME` is set: Uses PostgreSQL with `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- If `DB_NAME` is not set: Uses SQLite (default for quick setup)

See [Getting Started](getting-started.md#3-database-setup) for setup instructions.

### `urls.py`

The root URL router. All app URLs are included here:

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", LoginView.as_view(), name="login"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("samples/", include("samples.urls")),
    path("", include("lims_core.urls")),
]
```

---

## Apps

Django apps are self-contained modules. Each app handles a specific feature.

### `accounts/` - User Management

Handles user authentication and profiles.

```
accounts/
├── __init__.py
├── models.py           # Custom User model
├── admin.py            # Admin panel customization
├── apps.py             # App configuration
├── migrations/         # Database migrations
└── templates/
    └── accounts/
        └── login.html  # Login page
```

**Key file - `models.py`:**

```python
class User(AbstractUser):
    """Custom user model with SSO-ready fields."""
    external_id = models.CharField(max_length=255, blank=True)  # For SSO
    employee_id = models.CharField(max_length=50, blank=True)   # University ID
    department = models.CharField(max_length=100, blank=True)

    def display_name(self):
        """Returns best available display name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email or self.username
```

> **Why a custom User model?** It's much easier to add fields now than to migrate later. The `external_id` field will be used for SSO integration.

### `lims_core/` - Core Infrastructure

Shared templates, base layouts, and utility views.

```
lims_core/
├── __init__.py
├── apps.py
├── urls.py
├── views.py            # Home page view
├── migrations/
└── templates/
    └── lims_core/
        ├── base.html   # Master template (all pages extend this)
        ├── home.html   # Landing page
        └── partials/
            └── toast.html  # Notification component
```

**Key file - `base.html`:**

This is the master template. All pages extend it:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}WuLims{% endblock %}</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg">
        <!-- ... navbar content ... -->
    </nav>

    <!-- Toast container for notifications -->
    <div id="toast-container">
        <div id="toast-target"></div>
    </div>

    <!-- Main content -->
    <main class="container mt-4">
        {% block content %}{% endblock %}
    </main>

    <!-- Scripts -->
    <script src="https://unpkg.com/htmx.org@1.9.12"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

### `samples/` - Sample Management

The main LIMS functionality - tracking and managing samples.

```
samples/
├── __init__.py
├── models.py           # Sample model with status workflow
├── views.py            # List, detail, and approval views
├── urls.py             # URL routing
├── forms.py            # Filter forms
├── admin.py            # Admin panel configuration
├── apps.py
├── migrations/
└── templates/
    └── samples/
        ├── sample_list.html    # Main worklist page
        ├── sample_detail.html  # Sample detail page
        └── partials/           # HTMX partial templates
            ├── sample_table.html
            ├── sample_row.html
            ├── sample_filters.html
            ├── sample_overview.html
            ├── sample_chain_of_custody.html
            └── approve_modal.html
```

**Key file - `models.py`:**

```python
class Sample(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "RECEIVED", "Received"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        IN_REVIEW = "IN_REVIEW", "In Review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    sample_id = models.CharField(max_length=50, unique=True)
    client_name = models.CharField(max_length=200)
    received_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECEIVED)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
```

---

## Static Files (`static/`)

Static assets like CSS, JavaScript, and images.

```
static/
├── css/
│   └── styles.css      # Custom styles
├── js/
│   └── app.js          # Custom JavaScript
└── images/
    └── logo.png
```

Reference static files in templates:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/styles.css' %}">
<img src="{% static 'images/logo.png' %}" alt="Logo">
```

---

## Templates

Templates follow a consistent organization:

```
app_name/
└── templates/
    └── app_name/           # Namespaced to avoid conflicts
        ├── page.html       # Full pages (extend base.html)
        └── partials/       # HTMX fragments (no base template)
            └── component.html
```

### Template Types

1. **Full Pages** - Extend `base.html`, have complete HTML structure
2. **Partials** - HTML fragments returned by HTMX endpoints, no `{% extends %}`

---

## File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Apps | lowercase, singular | `samples`, `accounts` |
| Models | PascalCase, singular | `Sample`, `User` |
| Views | snake_case, descriptive | `sample_list`, `approve_sample` |
| URLs | lowercase with hyphens | `/samples/`, `/approve-sample/` |
| Templates | snake_case.html | `sample_list.html` |
| HTMX endpoints | underscore prefix in URL | `/_table/`, `/_modal/` |

---

## Adding a New App

When you need to add new functionality:

```bash
# Create the app
python manage.py startapp inventory

# Add to settings.py INSTALLED_APPS
INSTALLED_APPS = [
    # ...
    "inventory",
]

# Create app structure
inventory/
├── models.py       # Define your models
├── views.py        # Define your views
├── urls.py         # Define URL patterns (create this file)
├── admin.py        # Register models with admin
└── templates/
    └── inventory/
        └── (your templates)

# Include URLs in config/urls.py
path("inventory/", include("inventory.urls")),
```

---

## Next Steps

- Read [Architecture](architecture.md) to understand HTMX patterns
- Read [Creating Views](creating-views.md) to add new features
