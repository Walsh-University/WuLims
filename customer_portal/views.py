from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404

from accounts.views import is_customer_contact
from customer_portal.forms import CompanyProfileForm, ContactProfileForm, ProjectRequestForm
from customer_portal.models import ProjectRequest


def _get_customer_for_user(user):
    """Get the customer associated with the logged-in user."""
    customer = getattr(user, "customer_profile", None)
    if not customer:
        return None
    return customer


def _check_customer_access(request, customer_id):
    """Check if user has access to view/modify this customer's data."""
    user_customer = _get_customer_for_user(request.user)
    if not user_customer or user_customer.customer_id != customer_id:
        raise Http404("Access denied")


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


@login_required
def project_request_create(request):
    """Create a new project request."""
    if not is_customer_contact(request.user):
        raise Http404("Access denied")

    customer = _get_customer_for_user(request.user)
    if not customer:
        return redirect("customer_portal:company_profile")

    contact = request.user.contact_profile
    if not contact:
        return redirect("customer_portal:contact_profile")

    if request.method == "POST":
        form = ProjectRequestForm(request.POST)
        if form.is_valid():
            project_request = form.save(commit=False)
            project_request.customer = customer
            project_request.requesting_contact = contact
            project_request.save()
            return redirect("customer_portal:project_request_confirmation", request_id=project_request.request_id)
    else:
        form = ProjectRequestForm()

    return render(
        request,
        "customer_portal/project_request_form.html",
        {
            "form": form,
            "company_profile": customer,
            "contact_profile": contact,
        },
    )


@login_required
def project_request_confirmation(request, request_id):
    """Display confirmation page after project request submission."""
    if not is_customer_contact(request.user):
        raise Http404("Access denied")

    customer = _get_customer_for_user(request.user)
    if not customer:
        raise Http404("Access denied")

    project_request = get_object_or_404(ProjectRequest, request_id=request_id)

    # Check tenant access: ensure user's customer owns this request
    if project_request.customer_id != customer.customer_id:
        raise Http404("Access denied")

    return render(
        request,
        "customer_portal/project_request_confirmation.html",
        {
            "project_request": project_request,
            "company_profile": customer,
        },
    )


@login_required
def project_request_list(request):
    """List project requests for the authenticated customer."""
    if not is_customer_contact(request.user):
        raise Http404("Access denied")

    customer = _get_customer_for_user(request.user)
    if not customer:
        raise Http404("Access denied")

    # Tenant isolation: only show requests for this customer
    project_requests = ProjectRequest.objects.filter(customer=customer)

    return render(
        request,
        "customer_portal/project_request_list.html",
        {
            "project_requests": project_requests,
            "company_profile": customer,
        },
    )
