from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils import timezone

from .forms import SampleFilterForm
from .models import Sample


@login_required
def sample_list(request):
    form = SampleFilterForm(request.GET or None)
    return render(request, "samples/sample_list.html", {"form": form})


@login_required
def sample_table(request):
    form = SampleFilterForm(request.GET or None)
    qs = Sample.objects.all().order_by("-received_at")

    if form.is_valid():
        status = form.cleaned_data.get("status")
        q = form.cleaned_data.get("q")
        if status:
            qs = qs.filter(status=status)
        if q:
            qs = qs.filter(sample_id__icontains=q) | qs.filter(client_name__icontains=q)

    return render(request, "samples/partials/sample_table.html", {"samples": qs, "form": form})


@login_required
def sample_detail(request, pk: int):
    sample = get_object_or_404(Sample, pk=pk)
    tab = request.GET.get("tab")

    if tab == "overview":
        return render(request, "samples/partials/sample_overview.html", {"sample": sample})
    if tab == "coc":
        return render(request, "samples/partials/sample_chain_of_custody.html", {"sample": sample})

    return render(request, "samples/sample_detail.html", {"sample": sample})


@login_required
def approve_modal(request, pk: int):
    sample = get_object_or_404(Sample, pk=pk)
    return render(request, "samples/partials/approve_modal.html", {"sample": sample})


@login_required
def approve_sample(request, pk: int):
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


def sample_add():
    pass
