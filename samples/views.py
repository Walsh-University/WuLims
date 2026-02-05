import uuid

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import CharField, Q
from django.db.models.functions import Cast
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone

from .forms import SampleFilterForm, SampleForm
from .models import Sample


@login_required
@permission_required("samples.view_sample", raise_exception=True)
def sample_list(request):
    form = SampleFilterForm(request.GET or None)
    return render(request, "samples/sample_list.html", {"form": form})


@login_required
@permission_required("samples.view_sample", raise_exception=True)
def sample_table(request):
    form = SampleFilterForm(request.GET or None)
    qs = Sample.objects.all().order_by("-received_at")

    if form.is_valid():
        status = form.cleaned_data.get("status")
        q = form.cleaned_data.get("q")
        if status:
            qs = qs.filter(status=status)
        if q:
            qs = qs.annotate(sample_id_str=Cast("sample_id", output_field=CharField()))
            qs = qs.filter(Q(sample_id_str__icontains=q) | Q(client_name__icontains=q))

    return render(request, "samples/partials/sample_table.html", {"samples": qs, "form": form})


@login_required
@permission_required("samples.view_sample", raise_exception=True)
def sample_detail(request, pk: uuid.UUID):
    sample = get_object_or_404(Sample, pk=pk)
    tab = request.GET.get("tab")

    if tab == "overview":
        return render(request, "samples/partials/sample_overview.html", {"sample": sample})
    if tab == "coc":
        return render(request, "samples/partials/sample_chain_of_custody.html", {"sample": sample})

    return render(request, "samples/sample_detail.html", {"sample": sample})


@login_required
@permission_required("samples.approve_sample", raise_exception=True)
def approve_modal(request, pk: uuid.UUID):
    sample = get_object_or_404(Sample, pk=pk)
    return render(request, "samples/partials/approve_modal.html", {"sample": sample})


@login_required
@permission_required("samples.approve_sample", raise_exception=True)
def approve_sample(request, pk: uuid.UUID):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    sample = get_object_or_404(Sample, pk=pk)

    if sample.status != Sample.Status.IN_REVIEW:
        return HttpResponseBadRequest("Sample must be IN_REVIEW to approve.")

    sample.status = Sample.Status.APPROVED
    sample.approved_at = timezone.now()
    sample.approved_by = request.user
    sample.save()

    row_html = render_to_string("samples/partials/sample_row.html", {"s": sample}, request=request)
    toast_html = render_to_string(
        "lims_core/partials/toast.html",
        {"message": f"Sample {sample.sample_id} approved.", "level": "success"},
        request=request,
    )

    # Out-of-band swaps: add toast + clear modal content
    oob = toast_html + '<div id="modal-target" hx-swap-oob="innerHTML"></div>'

    return HttpResponse((row_html + oob).encode("utf-8"))


@login_required
@permission_required("samples.add_sample", raise_exception=True)
def sample_add(request):
    if request.method == "POST":
        form = SampleForm(request.POST)
        if form.is_valid():
            sample = form.save()
            return redirect("samples:detail", pk=sample.pk)
    else:
        form = SampleForm()

    return render(request, "samples/sample_form.html", {"form": form})
