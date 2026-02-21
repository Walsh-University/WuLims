from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string

from audit.models import AuditEvent

from .forms import ExperimentFilterForm
from .models import Experiment


@login_required
def experiment_list(request):
    form = ExperimentFilterForm(request.GET or None)
    return render(request, "experiments/experiment_list.html", {"form": form})


@login_required
def experiment_table(request):
    form = ExperimentFilterForm(request.GET or None)
    qs = Experiment.objects.all().order_by("name")

    if form.is_valid():
        q = form.cleaned_data.get("q")
        is_active = form.cleaned_data.get("is_active")

        if is_active in ["True", "False"]:
            qs = qs.filter(is_active=is_active == "True")

        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(description__icontains=q)

    return render(
        request,
        "experiments/partials/experiment_table.html",
        {"experiments": qs, "form": form},
    )


@login_required
def experiment_detail(request, pk: int):
    experiment = get_object_or_404(Experiment, pk=pk)
    return render(
        request,
        "experiments/experiment_detail.html",
        {"experiment": experiment},
    )


@login_required
def experiment_detail_tab(request, pk: int):
    experiment = get_object_or_404(Experiment, pk=pk)
    tab = request.GET.get("tab", "overview")

    if tab == "audit":
        content_type = ContentType.objects.get_for_model(Experiment)

        audit_timeline = AuditEvent.objects.filter(
            object_type=content_type,
            object_id=str(experiment.pk),
        ).order_by("-timestamp")

        return render(
            request,
            "experiments/partials/experiment_audit.html",
            {
                "experiment": experiment,
                "audit_timeline": audit_timeline,
            },
        )

    return render(
        request,
        "experiments/partials/experiment_overview.html",
        {"experiment": experiment},
    )


@login_required
def toggle_active(request, pk: int):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    experiment = get_object_or_404(Experiment, pk=pk)

    experiment.is_active = not experiment.is_active
    experiment.save()

    row_html = render_to_string(
        "experiments/partials/experiment_row.html",
        {"exp": experiment},
        request=request,
    )

    toast_html = render_to_string(
        "lims_core/partials/toast.html",
        {"message": f"Experiment {experiment.name} updated.", "level": "success"},
        request=request,
    )

    oob = toast_html + '<div id="modal-target" hx-swap-oob="innerHTML"></div>'
    return HttpResponse((row_html + oob).encode("utf-8"))
