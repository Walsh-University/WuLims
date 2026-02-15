from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import CharField, Q
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ResultForm, ResultsFilterForm
from .models import Result


@login_required
@permission_required("results.view_result", raise_exception=True)
def results_list(request):
    form = ResultsFilterForm(request.GET or None)
    return render(request, "results/results_list.html", {"form": form})


@login_required
@permission_required("results.add_result", raise_exception=True)
def result_add(request):
    if request.method == "POST":
        form = ResultForm(request.POST)
        if form.is_valid():
            result = form.save()
            return redirect("results:detail", pk=result.pk)
    else:
        form = ResultForm()

    return render(request, "results/result_add.html", {"form": form})


@login_required
@permission_required("results.edit_result", raise_exception=True)
def results_edit(request):
    pass


@login_required
@permission_required("results.view_result", raise_exception=True)
def result_detail(request, pk):
    result = get_object_or_404(Result.objects.select_related("project", "sample"), pk=pk)
    tab = request.GET.get("tab")

    if tab == "overview":
        return render(request, "results/partials/result_overview.html", {"result": result})

    return render(request, "results/result_detail.html", {"result": result})


@login_required
@permission_required("results.view_result", raise_exception=True)
def results_table(request):
    form = ResultsFilterForm(request.GET or None)
    qs = Result.objects.select_related("project", "sample").all()

    if form.is_valid():
        status = form.cleaned_data.get("status")
        q = form.cleaned_data.get("q")
        if status:
            qs = qs.filter(status=status)
        if q:
            qs = qs.annotate(id_str=Cast("id", output_field=CharField()))
            qs = qs.filter(Q(id_str__icontains=q) | Q(project__name__icontains=q))

    return render(request, "results/partials/results_table.html", {"results": qs, "form": form})


@login_required
@permission_required("results.approve_result", raise_exception=True)
def approve_modal(request, pk):
    result = get_object_or_404(Result, pk=pk)
    return render(request, "results/partials/approve_modal.html", {"result": result})
