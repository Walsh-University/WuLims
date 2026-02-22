import uuid

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import CharField, Q
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomerFilterForm, CustomerForm
from .models import Customer


@login_required
@permission_required("customers.view_customer", raise_exception=True)
def customer_list(request):
    form = CustomerFilterForm(request.GET or None)
    return render(request, "customers/customer_list.html", {"form": form})


@login_required
@permission_required("customers.view_customer", raise_exception=True)
def customer_table(request):
    form = CustomerFilterForm(request.GET or None)
    qs = Customer.objects.all().order_by("-created_at")

    if form.is_valid():
        is_active = form.cleaned_data.get("is_active")
        q = form.cleaned_data.get("q")
        if is_active:
            qs = qs.filter(is_active=is_active)
        if q:
            qs = qs.annotate(customer_id_str=Cast("customer_id", output_field=CharField()))
            qs = qs.filter(Q(customer_id_str__icontains=q) | Q(customer_name__icontains=q))

    return render(request, "customers/partials/customer_table.html", {"customers": qs, "form": form})


@login_required
@permission_required("customers.view_customer", raise_exception=True)
def customer_detail(request, pk: uuid.UUID):
    customer = get_object_or_404(Customer, pk=pk)
    tab = request.GET.get("tab")

    if tab == "overview":
        return render(request, "customers/partials/customer_overview.html", {"customer": customer})

    return render(request, "customers/customer_detail.html", {"customer": customer})


@login_required
@permission_required("customers.add_customer", raise_exception=True)
def customer_add(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            return redirect("customers:detail", pk=customer.pk)
    else:
        form = CustomerForm()

    return render(request, "customers/customer_form.html", {"form": form})
