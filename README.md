![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white)
![Alpine.js](https://img.shields.io/badge/alpinejs-white.svg?style=for-the-badge&logo=alpinedotjs&logoColor=%238BC0D0)
![uv](https://img.shields.io/badge/uv-%23DE5FE9.svg?style=for-the-badge&logo=uv&logoColor=white)
![Argo CD](https://img.shields.io/badge/Argo%20CD-1e0b3e?style=for-the-badge&logo=argo&logoColor=#d16044)

![Build Status](https://github.com/walsh-university/WuLims/actions/workflows/test.yml/badge.svg)

# WuLims (Walsh University LIMS)

WuLims is a student-built Laboratory Information Management System (LIMS) built with Django, HTMX, and Bootstrap.

## App Overview

WuLims is designed to be:

1. Student-led for learning full-stack development with real workflows
2. Enterprise-ready with a custom user model and role-based permissions
3. OIDC authentication
4. Sample tracking, chain-of-custody, Experiments, QA, review and approval gates, Reporting

## Core Features

- Sample
- Results
- Approval flow with modal actions and UI feedback (row update + toast)
- Custom user model (`accounts.User`) ready for AD/SSO integration
- Groups and permissions ready for role-based workflows
- Customers
- Projects
- Experiments
- Results
- Reporting

## Tech Stack

- Python 3.13+
- Django 6.0+
- HTMX
- Alpine.js
- Bootstrap 5.3
- PostgreSQL
- Kubernetes ready
- uv for Python environment and dependency management

## Student Contributors

Dev Team:

| Contributor      | GitHub                                                     | Notes |
|------------------|------------------------------------------------------------| --- |
| David Good       | [@programminggoody](https://github.com/programminggoody)   | Faculty Advisor      |
| Logan Trent      | [@logantrent](https://github.com/logantrent)               | Core app development |
| Payton McCord   | [@pmccord2003](https://github.com/pmccord2003)             | Core app development |
| Olesia Ivashchuk | [@olesyaivashchuk24](https://github.com/olesyaivashchuk24) | Core app development |
| Joey Timco       | [@jatimco7](https://github.com/jatimco7)                   | Core app development |

## Quick Start

```bash
uv venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows PowerShell

uv sync
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then visit:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/samples/
- http://127.0.0.1:8000/admin/

## Notes

- Custom user model is enabled from day 1 (`AUTH_USER_MODEL = "accounts.User"`).
- Groups/permissions are ready for role-based workflows (reviewer approvals, etc.).
- For AD/SSO later: prefer OIDC (Azure AD/Entra or ADFS OIDC) or SAML2 (common in higher-ed).
- Developer documentation is in `docs/README.md`.

## Observability (Structured Logging + OpenTelemetry)

WuLims now emits structured JSON logs by default and can export traces to SigNoz over OTLP.

- Structured JSON logs:
  - `DJANGO_JSON_LOGS=1` (default)
  - `DJANGO_LOG_LEVEL=INFO` (default)
- OpenTelemetry tracing:
  - `OTEL_ENABLED=1` (default)
  - `OTEL_EXPORTER_OTLP_ENDPOINT` or `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` (required to export traces)
  - `OTEL_EXPORTER_OTLP_INSECURE=1` (default, useful for in-cluster collector traffic)
  - `OTEL_EXPORTER_OTLP_HEADERS` (optional, `key=value,key2=value2`)
  - `OTEL_SERVICE_NAME` (default: `wulims`)
  - `OTEL_SERVICE_NAMESPACE` (default: `wulims`)
  - `OTEL_SERVICE_VERSION` (default: `0.1.0`)
  - `OTEL_ENVIRONMENT` (default: `production`)

Kubernetes: set OTLP endpoint to your SigNoz collector service.

Single Docker container: app remains fully usable without OTLP endpoint; traces are simply not exported while structured logs still go to stdout.
