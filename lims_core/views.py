from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from instruments.models import Instrument
from samples.models import Sample


@login_required
def home(request):
    return render(request, "lims_core/home.html")


@login_required
def dashboard(request):
    instruments_online = Instrument.objects.filter(is_active=True).count()
    samples_received = Sample.objects.filter(status=Sample.Status.RECEIVED).count()
    return render(
        request,
        "lims_core/dashboard.html",
        {"instruments_online": instruments_online, "samples_received": samples_received},
    )


def search(request):
    q = (request.GET.get("q") or "").strip()
    # Later: search Customers/Projects/Experiments/Samples
    return render(request, "lims_core/search.html", {"q": q})
