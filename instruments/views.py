from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string

from .forms import InstrumentFilterForm
from .models import Instrument


@login_required
def instrument_list(request):
    form = InstrumentFilterForm(request.GET or None)
    return render(request, "instruments/instrument_list.html", {"form": form})


@login_required
def instrument_table(request):
    form = InstrumentFilterForm(request.GET or None)
    qs = Instrument.objects.all().order_by("name")

    if form.is_valid():
        q = form.cleaned_data.get("q")
        is_active = form.cleaned_data.get("is_active")
        manufacturer = form.cleaned_data.get("manufacturer")

        if is_active in ["True", "False"]:
            qs = qs.filter(is_active=is_active == "True")
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(description__icontains=q)
        if manufacturer:
            qs = qs.filter(manufacturer__icontains=manufacturer)

    return render(
        request,
        "instruments/partials/instrument_table.html",
        {"instruments": qs, "form": form}
    )


@login_required
def instrument_detail(request, pk: int):
    instrument = get_object_or_404(Instrument, pk=pk)
    return render(request, "instruments/instrument_detail.html", {"instrument": instrument})


@login_required
def toggle_active(request, pk: int):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    instrument = get_object_or_404(Instrument, pk=pk)
    instrument.is_active = not instrument.is_active
    instrument.save()

    row_html = render_to_string(
        "instruments/partials/instrument_row.html", {"i": instrument}, request=request
    )

    toast_html = render_to_string(
        "lims_core/partials/toast.html",
        {"message": f"Instrument {instrument.name} updated.", "level": "success"},
        request=request,
    )

    oob = toast_html + '<div id="modal-target" hx-swap-oob="innerHTML"></div>'
    return HttpResponse((row_html + oob).encode("utf-8"))
