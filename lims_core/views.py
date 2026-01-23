from django.contrib.auth.decorators import login_required
from django.shortcuts import render


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
