from django.contrib.auth import get_user_model

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "Lab Tech": {
        "samples.view_sample",
        "results.view_result",
    },
    "Analyst": {
        "samples.view_sample",
        "samples.change_sample",
        "results.view_result",
        "results.change_result",
        "results.submit_result",
    },
    "QA Reviewer": {
        "samples.view_sample",
        "samples.approve_sample",
        "results.view_result",
        "results.approve_result",
        "results.reject_result",
    },
    "Lab Manager": {
        "samples.view_sample",
        "samples.add_sample",
        "samples.change_sample",
        "samples.delete_sample",
        "samples.approve_sample",
        "results.view_result",
        "results.add_result",
        "results.change_result",
        "results.submit_result",
        "results.delete_result",
        "results.approve_result",
        "results.reject_result",
    },
    "Customer Contact": {
        "samples.view_sample",
        "results.view_result",
    },
    "System Admin": {
        "accounts.manage_roles",
        "samples.view_sample",
        "samples.add_sample",
        "samples.change_sample",
        "samples.delete_sample",
        "samples.approve_sample",
        "results.view_result",
        "results.add_result",
        "results.change_result",
        "results.submit_result",
        "results.delete_result",
        "results.approve_result",
        "results.reject_result",
    },
}


def resolve_manage_roles_permission_codename() -> str:
    user_model = get_user_model()
    return f"{user_model._meta.app_label}.manage_roles"
