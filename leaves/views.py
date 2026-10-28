from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import LeaveRequestForm
from .models import LeaveEntitlement, LeaveRequest


@login_required
def dashboard(request):
    """
    Entry point after login.
    Employees go to My Requests, Admins stay on the dashboard.
    """
    if request.user.is_employee:
        return redirect("leaves:my_requests")
    return render(request, "leaves/dashboard.html")


@login_required
def my_requests(request):
    if request.user.is_admin:
        return redirect("leaves:dashboard")  # ← fixed incomplete redirect

    # Get entitlements for the employee's company
    entitlements = LeaveEntitlement.objects.filter(
        company=request.user.company
    ).select_related("leave_type")

    # Get all leave requests of the current user
    requests = (
        LeaveRequest.objects.filter(employee=request.user)
        .select_related("leave_type")
        .order_by("-created_at")
    )

    # Simple balance calculation
    balances = []
    for ent in entitlements:
        if ent.leave_type.code == "unpaid":
            continue

        used_days = sum(
            r.duration_days
            for r in requests
            if r.leave_type == ent.leave_type
            and r.status == LeaveRequest.Status.APPROVED
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
        "requests": requests,
        "pending_count": requests.filter(status=LeaveRequest.Status.PENDING).count(),
        "approved_count": requests.filter(status=LeaveRequest.Status.APPROVED).count(),
        "rejected_count": requests.filter(status=LeaveRequest.Status.REJECTED).count(),
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
        messages.success(
            self.request, "Request submitted. Your admin has been notified."
        )
        return super().form_valid(form)
