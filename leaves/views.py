from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView

from .emails import send_decision_email, send_new_request_email, send_nudge_email
from .forms import LeaveRequestForm
from .models import LeaveEntitlement, LeaveRequest


@login_required
def dashboard(request):
    if request.user.is_employee:
        return redirect("leaves:my_requests")

    # Pending requests for this admin’s company
    pending_requests = (
        LeaveRequest.objects.filter(
            employee__company=request.user.company,
            status=LeaveRequest.Status.PENDING,
        )
        .select_related("employee", "leave_type")
        .order_by("created_at")
    )

    # Simple stats
    approved_this_month = LeaveRequest.objects.filter(
        employee__company=request.user.company,
        status=LeaveRequest.Status.APPROVED,
        decided_at__month=timezone.now().month,
        decided_at__year=timezone.now().year,
    ).count()

    context = {
        "pending_requests": pending_requests,
        "pending_count": pending_requests.count(),
        "approved_this_month": approved_this_month,
    }
    return render(request, "leaves/dashboard.html", context)


@login_required
def my_requests(request):
    if request.user.is_admin:
        return redirect("leaves:dashboard")

    status_filter = request.GET.get("status", "all")

    entitlements = LeaveEntitlement.objects.filter(
        company=request.user.company
    ).select_related("leave_type")

    requests_qs = (
        LeaveRequest.objects.filter(employee=request.user)
        .select_related("leave_type")
        .order_by("-created_at")
    )

    # Counts for the tabs
    all_count = requests_qs.count()
    pending_count = requests_qs.filter(status=LeaveRequest.Status.PENDING).count()
    approved_count = requests_qs.filter(status=LeaveRequest.Status.APPROVED).count()
    rejected_count = requests_qs.filter(status=LeaveRequest.Status.REJECTED).count()

    # Apply filter
    if status_filter == "pending":
        requests_qs = requests_qs.filter(status=LeaveRequest.Status.PENDING)
    elif status_filter == "approved":
        requests_qs = requests_qs.filter(status=LeaveRequest.Status.APPROVED)
    elif status_filter == "rejected":
        requests_qs = requests_qs.filter(status=LeaveRequest.Status.REJECTED)

    # Balance cards
    balances = []
    for ent in entitlements:
        if ent.leave_type.code == "unpaid":
            continue

        used_days = sum(
            r.duration_days
            for r in LeaveRequest.objects.filter(
                employee=request.user,
                leave_type=ent.leave_type,
                status=LeaveRequest.Status.APPROVED,
            )
        )
        remaining = max(ent.days_per_year - used_days, 0)

        balances.append(
            {
                "leave_type": ent.leave_type,
                "total": ent.days_per_year,
                "used": used_days,
                "remaining": remaining,
                "percent_used": (used_days / ent.days_per_year * 100)
                if ent.days_per_year > 0
                else 0,
            }
        )

    context = {
        "balances": balances,
        "requests": requests_qs,
        "status_filter": status_filter,
        "all_count": all_count,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
    }
    return render(request, "leaves/my_requests.html", context)


class NewLeaveRequestView(CreateView, LoginRequiredMixin):
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = "leaves/new_request.html"
    success_url = reverse_lazy("leaves:my_requests")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_admin:
            return redirect("leaves:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.employee = self.request.user
        response = super().form_valid(form)
        send_new_request_email(self.object, self.request)
        messages.success(
            self.request, "Request submitted. Your admin has been notified."
        )
        return response


@login_required
@require_POST
def approve_request(request, pk):
    if not request.user.is_admin:
        return redirect("leaves:my_requests")

    leave_request = get_object_or_404(
        LeaveRequest,
        pk=pk,
        employee__company=request.user.company,
        status=LeaveRequest.Status.PENDING,
    )

    leave_request.status = LeaveRequest.Status.APPROVED
    leave_request.reviewer = request.user
    leave_request.decided_at = timezone.now()
    leave_request.reviewer_comment = request.POST.get("comment", "")
    leave_request.save()
    send_decision_email(leave_request, request)

    name = leave_request.employee.get_full_name() or leave_request.employee.email
    messages.success(
        request,
        f"Request approved. {name} has been notified.",
    )
    return redirect("leaves:dashboard")


@login_required
@require_POST
def reject_request(request, pk):
    if not request.user.is_admin:
        return redirect("leaves:my_requests")

    leave_request = get_object_or_404(
        LeaveRequest,
        pk=pk,
        employee__company=request.user.company,
        status=LeaveRequest.Status.PENDING,
    )

    leave_request.status = LeaveRequest.Status.REJECTED
    leave_request.reviewer = request.user
    leave_request.decided_at = timezone.now()
    leave_request.reviewer_comment = request.POST.get("comment", "")
    leave_request.save()
    send_decision_email(leave_request, request)

    messages.success(request, "Request rejected.")
    return redirect("leaves:dashboard")


@login_required
def all_requests(request):
    if not request.user.is_admin:
        return redirect("leaves:my_requests")

    status_filter = request.GET.get("status", "all")

    requests_qs = (
        LeaveRequest.objects.filter(employee__company=request.user.company)
        .select_related("employee", "leave_type", "reviewer")
        .order_by("-created_at")
    )

    all_count = requests_qs.count()
    pending_count = requests_qs.filter(status=LeaveRequest.Status.PENDING).count()
    approved_count = requests_qs.filter(status=LeaveRequest.Status.APPROVED).count()
    rejected_count = requests_qs.filter(status=LeaveRequest.Status.REJECTED).count()

    if status_filter == "pending":
        requests_qs = requests_qs.filter(status=LeaveRequest.Status.PENDING)
    elif status_filter == "approved":
        requests_qs = requests_qs.filter(status=LeaveRequest.Status.APPROVED)
    elif status_filter == "rejected":
        requests_qs = requests_qs.filter(status=LeaveRequest.Status.REJECTED)

    context = {
        "requests": requests_qs,
        "status_filter": status_filter,
        "all_count": all_count,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
    }
    return render(request, "leaves/all_requests.html", context)


@login_required
@require_POST
def nudge_request(request, pk):
    leave_request = get_object_or_404(
        LeaveRequest,
        pk=pk,
        employee=request.user,
        status=LeaveRequest.Status.PENDING,
    )

    # Cooldown: can only nudge once every 48 hours
    if leave_request.last_nudged_at:
        cooldown = leave_request.last_nudged_at + timedelta(hours=48)
        if timezone.now() < cooldown:
            messages.warning(request, "You can only nudge once every 48 hours.")
            return redirect("leaves:my_requests")

    leave_request.nudge_count += 1
    leave_request.last_nudged_at = timezone.now()
    leave_request.save(update_fields=["nudge_count", "last_nudged_at"])

    # Notify admins
    send_nudge_email(leave_request, request)

    messages.success(request, "Nudge sent. Your admin has been reminded.")
    return redirect("leaves:my_requests")
