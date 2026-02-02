![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![Build Status](https://github.com/walsh-university/WuLims/actions/workflows/test.yml/badge.svg)

# WuLims (Django + HTMX + Bootstrap starter)

A student-friendly starter for a LIMS-style app using:
- Django (sessions/auth)
- HTMX (partial updates)
- Bootstrap 5 (UI)
- Custom User model (`accounts.User`) to make future AD/SSO integration easier
- Example `samples` module with:
    - Worklist page (filters + HTMX table)
    - Detail page with HTMX tabs
    - Approve flow (modal + row update + toast)

## Quick start

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
- http://127.0.0.1:8000/samples/
- http://127.0.0.1:8000/admin/

## Notes
- Custom user model is enabled from day 1 (`AUTH_USER_MODEL = "accounts.User"`).
- Groups/permissions are ready for role-based workflows (Reviewer approvals, etc).
- For AD/SSO later: prefer OIDC (Azure AD/Entra or ADFS OIDC) or SAML2 (common in higher-ed).
