from .models import LeaveRequest


def pending_count(request):
    if not request.user.is_authenticated or not request.user.is_admin:
        return {}

    count = LeaveRequest.objects.filter(
        employee__company=request.user.company,
        status=LeaveRequest.Status.PENDING,
    ).count()

    return {
        "pending_requests_count": count,
    }
