from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from projects.forms import ProjectFilterForm


@login_required
@permission_required("projects.view_project", raise_exception=True)
def project_list(request):
    form = ProjectFilterForm
    return render(request, "projects/project_list.html", {"form": form})
