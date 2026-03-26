from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import redirect, render

from projects.forms import ProjectFilterForm, ProjectForm, ProjectRequestForm
from projects.models import Project, ProjectRequest


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


@login_required
@permission_required("projects.add_project", raise_exception=True)
def project_add(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("projects:list")
    else:
        form = ProjectForm()

    return render(request, "projects/project_form.html", {"form": form})


@login_required
def project_request_create(request):
    if request.method == "POST":
        form = ProjectRequestForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)

            obj.customer_contact = request.user.customer_contact
            obj.status = "PENDING"

            obj.save()

            return redirect("projects:project_request_success", pk=obj.id)

    else:
        form = ProjectRequestForm()

    return render(request, "projects/project_request_form.html", {"form": form})


@login_required
def project_request_success(request, pk):
    obj = ProjectRequest.objects.get(id=pk)

    return render(request, "projects/project_request_success.html", {"project": obj})
