# Project Structure

This document reflects the current repository layout for WuLims.

## Top-Level Layout

```text
WuLims/
├── .github/                 # GitHub templates and CI/CD workflows
├── accounts/                # Custom user model, role/permission auditing
├── assets/                  # SCSS source files
├── config/                  # Django project config (settings, URLs, WSGI/ASGI)
├── customers/               # Customer domain models
├── docker/                  # Container and local Docker scripts
├── docs/                    # Developer documentation (MkDocs source)
├── experiments/             # Experiment domain models/app code
├── instruments/             # Instruments app (forms/views/templates)
├── lims_core/               # Shared core pages and status utilities
├── projects/                # Projects domain models
├── results/                 # Results workflow app
├── samples/                 # Sample intake and lifecycle app
├── scripts/                 # Utility scripts (for example seed SQL)
├── static/                  # Compiled/static assets served by Django
├── templates/               # Global template overrides (e.g., admin)
├── tests/                   # Pytest test suite
├── manage.py                # Django management entrypoint
├── mkdocs.yml               # MkDocs configuration
├── pyproject.toml           # Python dependencies and tool config
└── uv.lock                  # Locked dependency graph
```

## Django Configuration (`config/`)

```text
config/
├── settings.py              # Local/dev settings loader
├── settings/
│   ├── base.py              # Shared Django settings
│   ├── dev.py               # Development overrides
│   ├── prod.py              # Production overrides
│   └── test.py              # Test overrides (SQLite, fast hashing)
├── urls.py                  # Root URL router
├── observability.py         # Structured logging / telemetry config
├── asgi.py
└── wsgi.py
```

## Django Apps

### Accounts (`accounts/`)
- Custom `User` model
- Role assignment auditing and related signals
- Admin customization and auth templates

### LIMS Domain Apps
- `samples/`: sample tracking and workflow
- `results/`: result review/approval workflow
- `experiments/`: experiment entities
- `projects/`: project entities
- `customers/`: customer entities
- `instruments/`: instrument catalog/forms/views

### Core (`lims_core/`)
- Shared pages/utilities and core status helpers

Each app generally follows this pattern:

```text
app_name/
├── apps.py
├── models.py
├── views.py
├── urls.py                  # if app exposes routes
├── forms.py                 # if app has user input forms
├── admin.py
├── migrations/
└── templates/app_name/
```

## Frontend Assets

```text
assets/scss/                 # SCSS source
static/css/                  # Compiled CSS committed for runtime
static/js/                   # JS vendor/runtime bundles
templates/                   # Project-wide template overrides
```

## Docs and Publishing

- Source docs are in `docs/`
- MkDocs config is at `mkdocs.yml`
- GitHub Actions workflows are in `.github/workflows/`
  - CI checks (lint/type/tests/docs build)
  - Docs publish workflow

## Tests

```text
tests/
├── conftest.py
├── test_accounts.py
├── test_projects.py
├── test_samples.py
├── test_results.py
├── test_experiments.py
├── test_status.py
└── instruments/test_instruments.py
```

## Notes

- Ignore generated directories when navigating locally:
  - `site/` (MkDocs build output)
  - `htmlcov/` (coverage HTML)
  - `__pycache__/` and `.pytest_cache/`
