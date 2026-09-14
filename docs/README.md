# WuLims Developer Documentation

Welcome to the WuLims project! This is a Laboratory Information Management System (LIMS) built with Django, HTMX, and Bootstrap.

## Documentation Index

| Document                                  | Description                                               |
|-------------------------------------------|-----------------------------------------------------------|
| [Getting Started](getting-started.md)     | Environment setup, Django basics, and running the project |
| [Project Structure](project-structure.md) | Directory layout and file organization                    |
| [Architecture](architecture.md)           | HTMX patterns, template hierarchy, and design decisions   |
| [Django Relationships](Django-relationships.md) | Model relationship patterns and examples            |
| [Creating Views](creating-views.md)       | How to create new views and HTMX endpoints                |
| [Styling](styling.md)                     | SCSS, Bootstrap theming, and CSS build workflow           |
| [UI Conventions](ui-conventions.md)       | UI conventions for WuLims                       |
| [Testing](testing.md)                     | Running tests, coverage, and test-writing practices       |
| [Migrations](migrations.md)               | Database migrations and model changes                     |
| [Chain of Custody](chain_of_custody.md)   | Sample custody flow and auditability rules                |
| [Roles & Permissions](roles-and-permissions.md) | Default roles, group permissions, and enforcement rules |
| [SAML2 Setup](saml.md)                    | Configure Microsoft Entra SAML2 login                     |
| [Docker](docker.md)                       | Container setup and running WuLims in Docker              |
| [Debugging HTMX](debugging-htmx.md)       | Console logging, common request errors, and swap issues   |

## Build Docs (MkDocs)

From the repository root:

```bash
uv sync --group dev
uv run mkdocs serve
```

Build static docs:

```bash
uv run mkdocs build
```

## Tech Stack

- **Python 3.13+** - Programming language
- **Django 6.0** - Web framework
- **HTMX** - Dynamic HTML without JavaScript frameworks
- **Alpine.js** - Lightweight JavaScript for interactivity
- **Bootstrap 5.3** - CSS framework for styling
- **PostgreSQL** - Primary application database
- **uv** - Fast Python package manager (replaces pip)

## Quick Start

```bash
# Clone and enter the project
cd WuLims

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync

# Set up the database
python manage.py migrate

# Create an admin user
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

Then visit:
- http://127.0.0.1:8000/ - Home page
- http://127.0.0.1:8000/samples/ - Sample worklist
- http://127.0.0.1:8000/admin/ - Admin panel

## Project Goals

WuLims is designed to be:

1. **Student-friendly** - Easy to understand and extend
2. **Enterprise-ready** - Patterns that scale (custom User model, SSO-ready)
3. **Modern** - HTMX for dynamic UIs without SPA complexity
4. **Practical** - Real LIMS workflows (sample tracking, approvals)
