from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .status import get_system_status


@login_required
def home(request):
    return render(request, "lims_core/home.html")


@login_required
def dashboard(request):
    return render(request, "lims_core/dashboard.html")


def search(request):
    q = (request.GET.get("q") or "").strip()
    # Later: search Customers/Projects/Experiments/Samples
    return render(request, "lims_core/search.html", {"q": q})


@login_required
def status_public(request):
    # Customer-safe response (no internal details)
    return JsonResponse(get_system_status(include_internal=False))


@login_required
def status_internal(request):
    # Internal response (includes dependency details)
    # Optional: restrict further to staff
    if not request.user.is_staff:
        return JsonResponse({"detail": "Forbidden"}, status=403)

    return JsonResponse(get_system_status(include_internal=True))
