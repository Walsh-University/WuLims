![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white)
![Alpine.js](https://img.shields.io/badge/alpinejs-white.svg?style=for-the-badge&logo=alpinedotjs&logoColor=%238BC0D0)
![uv](https://img.shields.io/badge/uv-%23DE5FE9.svg?style=for-the-badge&logo=uv&logoColor=white)
![Argo CD](https://img.shields.io/badge/Argo%20CD-1e0b3e?style=for-the-badge&logo=argo&logoColor=#d16044)

![Build Status](https://github.com/walsh-university/WuLims/actions/workflows/test.yml/badge.svg)
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
