from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.views import is_customer_contact
from customer_portal.forms import CompanyProfileForm


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
    if not is_customer_contact(request.user):
        return redirect("customer_portal:home")

    customer = request.user.customer_profile

    if request.method == "POST":
        form = CompanyProfileForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save()
            if request.user.customer_profile_id != customer.pk:
                request.user.customer_profile = customer
                request.user.save(update_fields=["customer_profile"])
            return redirect("customer_portal:home")
    else:
        form = CompanyProfileForm(instance=customer)

    return render(
        request,
        "customer_portal/company_profile_form.html",
        {
            "form": form,
            "company_profile": customer,
        },
    )
