from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.views import is_customer_contact


@login_required
def home(request):
    return render(
        request,
        "customer_portal/index.html",
        {
            "is_customer_contact": is_customer_contact(request.user),
        },
    )
