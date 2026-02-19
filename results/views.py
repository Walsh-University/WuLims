import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db.models import CharField, Q
from django.db.models.functions import Cast
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone

from audit.diff import compute_diff
from audit.models import AuditEvent
from audit.services import log_audit_event

from .forms import ResultForm, ResultsFilterForm
from .models import Result

logger = logging.getLogger(__name__)


def _eligible_reviewers(exclude_user=None):
    User = get_user_model()
    reviewers = User.objects.filter(is_active=True).filter(
        Q(
            user_permissions__content_type__app_label="results",
            user_permissions__codename__in=["approve_result", "reject_result"],
        )
        | Q(
            groups__permissions__content_type__app_label="results",
            groups__permissions__codename__in=["approve_result", "reject_result"],
        )
    )
    if exclude_user is not None:
        reviewers = reviewers.exclude(pk=exclude_user.pk)
    return reviewers.distinct().order_by("username")


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
@permission_required("results.change_result", raise_exception=True)
def results_edit(request, pk):
    result = get_object_or_404(Result, pk=pk)

    if request.method == "POST":
        old_result = Result.objects.get(pk=result.pk)
        form = ResultForm(request.POST, instance=result)
        if form.is_valid():
            updated_result = form.save()
            diff = compute_diff(
                old=old_result,
                new=updated_result,
                fields=["title", "description", "status", "sample", "project"],
            )
            if diff:
                log_audit_event(
                    user=request.user,
                    action="updated",
                    instance=updated_result,
                    diff=diff,
                )
            return redirect("results:detail", pk=result.pk)
    else:
        form = ResultForm(instance=result)

    return render(request, "results/result_edit.html", {"form": form, "result": result})


@login_required
@permission_required("results.view_result", raise_exception=True)
def result_detail(request, pk):
    result = get_object_or_404(Result.objects.select_related("project", "sample"), pk=pk)
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
def approve_modal(request, pk):
    result = get_object_or_404(Result, pk=pk)
    can_approve = request.user.has_perm("results.approve_result")
    can_reject = request.user.has_perm("results.reject_result")
    if not (can_approve or can_reject):
        raise PermissionDenied

    return render(
        request,
        "results/partials/approve_modal.html",
        {"result": result, "can_approve": can_approve, "can_reject": can_reject},
    )


@login_required
@permission_required("results.submit_result", raise_exception=True)
def submit_modal(request, pk):
    result = get_object_or_404(Result, pk=pk)
    if result.status != Result.Status.DRAFT:
        return HttpResponseBadRequest("Result must be DRAFT to submit for review.")

    reviewers = _eligible_reviewers(exclude_user=request.user)
    return render(
        request,
        "results/partials/submit_modal.html",
        {"result": result, "reviewers": reviewers},
    )


def _result_row_response(request, result: Result, message: str, level: str = "success"):
    row_html = render_to_string("results/partials/results_row.html", {"r": result}, request=request)
    toast_html = render_to_string(
        "lims_core/partials/toast.html",
        {"message": message, "level": level},
        request=request,
    )
    oob = toast_html + '<div id="modal-target" hx-swap-oob="innerHTML"></div>'
    return HttpResponse((row_html + oob).encode("utf-8"))


@login_required
@permission_required("results.submit_result", raise_exception=True)
def submit_result(request, pk):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    result = get_object_or_404(Result, pk=pk)
    if result.status != Result.Status.DRAFT:
        return HttpResponseBadRequest("Result must be DRAFT to submit for review.")

    required_errors = []
    if not (result.title or "").strip():
        required_errors.append("title")
    if not (result.description or "").strip():
        required_errors.append("description")
    if result.sample_id is None:
        required_errors.append("sample")
    if result.project_id is None:
        required_errors.append("project")

    if required_errors:
        return HttpResponseBadRequest(
            f"Missing required fields before submission: {', '.join(required_errors)}."
        )

    old_result = Result.objects.get(pk=result.pk)

    reviewer_id = (request.POST.get("reviewer_id") or "").strip()
    reviewers = _eligible_reviewers(exclude_user=request.user)
    reviewer = reviewers.filter(pk=reviewer_id).first() if reviewer_id else reviewers.first()
    if reviewer is None:
        return HttpResponseBadRequest("No eligible reviewer available for assignment.")

    result.status = Result.Status.IN_REVIEW
    result.reviewer = reviewer
    result.approved_at = None
    result.approved_by = None
    result.rejected_at = None
    result.rejected_by = None

    result.save()

    diff = compute_diff(
        old=old_result,
        new=result,
        fields=["status", "reviewer"],
    )

    log_audit_event(
        user=request.user,
        action="status_changed",
        instance=result,
        diff=diff,
    )

    return _result_row_response(
        request,
        result,
        f"Result {result.id} submitted for review and assigned to {reviewer.get_username()}.",
    )


@login_required
@permission_required("results.approve_result", raise_exception=True)
def approve_result(request, pk):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    result = get_object_or_404(Result, pk=pk)
    if result.status != Result.Status.IN_REVIEW:
        return HttpResponseBadRequest("Result must be IN_REVIEW to approve.")

    old_result = Result.objects.get(pk=result.pk)

    result.status = Result.Status.APPROVED
    result.approved_at = timezone.now()
    result.approved_by = request.user
    result.rejected_at = None
    result.rejected_by = None
    result.save()

    diff = compute_diff(
        old=old_result,
        new=result,
        fields=["status", "approved_at", "approved_by"],
    )

    log_audit_event(
        user=request.user,
        action="status_changed",
        instance=result,
        diff=diff,
    )

    return _result_row_response(request, result, f"Result {result.id} approved.")


@login_required
@permission_required("results.reject_result", raise_exception=True)
def reject_result(request, pk):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    result = get_object_or_404(Result, pk=pk)
    if result.status != Result.Status.IN_REVIEW:
        return HttpResponseBadRequest("Result must be IN_REVIEW to reject.")

    old_result = Result.objects.get(pk=result.pk)

    result.status = Result.Status.REJECTED
    result.rejected_at = timezone.now()
    result.rejected_by = request.user
    result.approved_at = None
    result.approved_by = None
    result.save()

    diff = compute_diff(
        old=old_result,
        new=result,
        fields=["status", "rejected_at", "rejected_by"],
    )

    log_audit_event(
        user=request.user,
        action="status_changed",
        instance=result,
        diff=diff,
    )

    return _result_row_response(request, result, f"Result {result.id} rejected.", level="warning")


@login_required
@permission_required("results.view_result", raise_exception=True)
def result_detail_tab(request, pk: int):
    result = get_object_or_404(Result.objects.select_related("project", "sample"), pk=pk)
    tab = request.GET.get("tab", "overview")

    if tab == "audit":
        content_type = ContentType.objects.get_for_model(Result)

        audit_timeline = AuditEvent.objects.filter(
            object_type=content_type,
            object_id=str(result.pk),
        ).order_by("-timestamp")

        return render(
            request,
            "results/partials/audit_tab.html",
            {"audit_timeline": audit_timeline, "result": result},
        )

    return render(
        request,
        "results/partials/overview_tab.html",
        {"result": result},
    )
