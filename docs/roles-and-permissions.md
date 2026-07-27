# Roles and Permissions

WuLims uses Django's built-in `Group` + `Permission` model for role-based access control (RBAC).

## Read This First: What Django Creates Automatically

For every Django model, Django automatically creates these base permissions during `python manage.py migrate`:

- `add_<model>`
- `change_<model>`
- `delete_<model>`
- `view_<model>`

Example: for `samples.Sample`, Django creates:

- `samples.add_sample`
- `samples.change_sample`
- `samples.delete_sample`
- `samples.view_sample`

You only need to explicitly define permissions for actions outside that default CRUD/view set, such as workflow actions like:

- `samples.approve_sample`
- `results.approve_result`
- `results.reject_result`
- `accounts.manage_roles`

Those custom permissions are defined in each model's `Meta.permissions` and then created in the database by migrations.

Practical rule for contributors:

1. If the action is standard create/edit/delete/read, use Django's built-in permission.
2. If the action is domain-specific (approve/reject/assign/escalate/etc.), add a custom permission in `Meta.permissions`.
3. After permission changes, run migrations so `auth_permission` stays in sync.

## Baseline Roles

These roles are created by migration and are intended to be the default starting point:

- `Lab Tech`
- `Analyst`
- `QA Reviewer`
- `Lab Manager`
- `Customer Contact`
- `System Admin`

## Permission Model

WuLims uses both Django model permissions and custom workflow/admin permissions.

### Sample permissions (`samples.Sample`)

- `samples.view_sample`
- `samples.add_sample`
- `samples.change_sample`
- `samples.delete_sample`
- `samples.approve_sample` (custom)

### Account permissions (`accounts.User`)

- `accounts.manage_roles` (custom)

## Default Role-to-Permission Mapping

| Role | Default permissions |
|---|---|
| `Lab Tech` | `samples.view_sample` |
| `Analyst` | `samples.view_sample`, `samples.change_sample` |
| `QA Reviewer` | `samples.view_sample`, `samples.approve_sample` |
| `Lab Manager` | `samples.view_sample`, `samples.add_sample`, `samples.change_sample`, `samples.delete_sample`, `samples.approve_sample` |
| `Customer Contact` | `samples.view_sample` |
| `System Admin` | `accounts.manage_roles`, `samples.view_sample`, `samples.add_sample`, `samples.change_sample`, `samples.delete_sample`, `samples.approve_sample` |

## Enforcement Notes

- View endpoints require `samples.view_sample`.
- Add-sample flow requires `samples.add_sample`.
- Approve modal/approval actions require `samples.approve_sample`.
- Group/role administration is limited to superusers or users with `accounts.manage_roles`.
- Customer portal project and project-request views require the `Customer Contact` role and scope records to the user's linked company profile.
- Internal project screens remain separate from portal views and require internal Django project permissions such as `projects.view_project` or `projects.add_project`.

## Keeping Roles Synced

Role defaults are maintained in:

- `accounts/roles.py`
- `accounts/migrations/0003_seed_baseline_roles.py`
- `accounts/migrations/0004_sync_baseline_role_permissions.py`

After pulling changes that modify role defaults, run:

```bash
python manage.py migrate
```

## Role Administration Workflow (Admin UI)

Use Django admin to assign or adjust roles safely:

1. Sign in at `/admin/` with a superuser account (or an account with `accounts.manage_roles`).
2. Open **Accounts > Users** and select a user.
3. In the **Groups** field, assign one or more roles (`Lab Tech`, `QA Reviewer`, etc.).
4. Save the user record.
5. Confirm expected access by testing the relevant workflow (view/add/approve).

### Recommended Practices

- Prefer group assignment over direct user permissions.
- Keep users in the smallest set of roles needed (least privilege).
- Use baseline roles as-is when possible; avoid custom one-off groups unless required.
- Review role changes in the audit log (`RoleAssignmentAudit`) after sensitive updates.
- Use a separate non-admin test account to validate behavior.

### Common Pitfalls

- Granting direct `user_permissions` can bypass role intent.
- Leaving a user in multiple groups can unintentionally combine permissions.
- Assuming role defaults changed without running `python manage.py migrate`.

## Quick Verification (Shell)

```python
from django.contrib.auth.models import Group

for g in Group.objects.order_by("name"):
    perms = sorted(f"{p.content_type.app_label}.{p.codename}" for p in g.permissions.all())
    print(g.name, perms)
```
