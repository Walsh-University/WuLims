from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import render

from projects.forms import ProjectFilterForm
from projects.models import Project


@login_required
@permission_required("projects.view_project", raise_exception=True)
def project_list(request):
    form = ProjectFilterForm
    return render(request, "projects/project_list.html", {"form": form})


@login_required
@permission_required("projects.view_project", raise_exception=True)
def project_table(request):
    form = ProjectFilterForm(request.GET or None)
    qs = Project.objects.all().order_by("name")

    if form.is_valid():
        q = form.cleaned_data.get("q")
        status = form.cleaned_data.get("status")

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        if status in Project.Status.values:
            qs = qs.filter(status=status)

    return render(request, "projects/partials/project_table.html", {"projects": qs, "form": form})
