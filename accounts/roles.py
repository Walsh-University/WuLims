from django.contrib.auth import get_user_model

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "Lab Tech": {
        "samples.view_sample",
    },
    "Analyst": {
        "samples.view_sample",
        "samples.change_sample",
    },
    "QA Reviewer": {
        "samples.view_sample",
        "samples.approve_sample",
    },
    "Lab Manager": {
        "samples.view_sample",
        "samples.add_sample",
        "samples.change_sample",
        "samples.delete_sample",
        "samples.approve_sample",
    },
    "Customer Contact": {
        "samples.view_sample",
    },
    "System Admin": {
        "accounts.manage_roles",
        "samples.view_sample",
        "samples.add_sample",
        "samples.change_sample",
        "samples.delete_sample",
        "samples.approve_sample",
    },
}


def resolve_manage_roles_permission_codename() -> str:
    user_model = get_user_model()
    return f"{user_model._meta.app_label}.manage_roles"
