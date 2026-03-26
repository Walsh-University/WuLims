from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.views import is_customer_contact

from .forms import CompanyProfileForm, CustomerContactForm
from .models import CustomerContact


@login_required
def home(request):
    customer_contact = is_customer_contact(request.user)

    if customer_contact and request.user.customer_profile_id is None:
        return redirect("customer_portal:company_profile")

    return render(
        request,
        "customer_portal/index.html",
        {
            "is_customer_contact": customer_contact,
            "company_profile": request.user.customer_profile,
        },
    )


@login_required
def company_profile(request):
    if request.method == "POST":
        form = CompanyProfileForm(request.POST, instance=request.user.customer_profile)

        if form.is_valid():
            company = form.save()
            request.user.customer_profile = company
            request.user.save()

            return redirect("customer_portal:home")

    else:
        form = CompanyProfileForm(instance=request.user.customer_profile)

    return render(
        request,
        "customer_portal/company_profile.html",
        {"form": form},
    )


@login_required
def contact_profile(request):
    contact = CustomerContact.objects.filter(user=request.user).first()

    if request.method == "POST":
        form = CustomerContactForm(
            request.POST,
            instance=contact,
            user=request.user,
        )

        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.customer = request.user.customer_profile
            contact.save()

            return redirect("customer_portal:home")

    else:
        form = CustomerContactForm(
            instance=contact,
            user=request.user,
        )

    return render(
        request,
        "customer_portal/contact_profile.html",
        {"form": form},
    )
