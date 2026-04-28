from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.views import is_customer_contact
from customer_portal.forms import CompanyProfileForm, ContactProfileForm


@login_required
def home(request):
    customer_contact = is_customer_contact(request.user)

    if customer_contact and request.user.customer_profile_id is None:
        return redirect("customer_portal:company_profile")
    if customer_contact and request.user.contact_profile_id is None:
        return redirect("customer_portal:contact_profile")

    return render(
        request,
        "customer_portal/index.html",
        {
            "is_customer_contact": customer_contact,
            "company_profile": request.user.customer_profile,
            "contact_profile": request.user.contact_profile,
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


@login_required
def contact_profile(request):
    if not is_customer_contact(request.user):
        return redirect("customer_portal:home")
    if request.user.customer_profile_id is None:
        return redirect("customer_portal:company_profile")

    person = request.user.contact_profile

    if request.method == "POST":
        form = ContactProfileForm(request.POST, instance=person)
        if form.is_valid():
            person = form.save(commit=False)
            person.customer_id = request.user.customer_profile
            person.save()
            if request.user.contact_profile_id != person.pk:
                request.user.contact_profile = person
                request.user.save(update_fields=["contact_profile"])
            request.user.first_name = person.first_name
            request.user.last_name = person.last_name
            request.user.save(update_fields=["first_name", "last_name"])
            return redirect("customer_portal:home")
    else:
        initial = None
        if person is None:
            initial = {
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "is_active": True,
            }
        form = ContactProfileForm(instance=person, initial=initial)

    return render(
        request,
        "customer_portal/contact_profile_form.html",
        {
            "form": form,
            "contact_profile": person,
            "company_profile": request.user.customer_profile,
        },
    )
