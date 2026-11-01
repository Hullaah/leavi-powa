from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone


def send_new_request_email(leave_request, request):
    """Notify the company admins that a new leave request was submitted."""
    employee = leave_request.employee
    company = employee.company

    # Find all admins of this company
    admins = company.users.filter(role="admin")

    if not admins.exists():
        return

    dashboard_url = request.build_absolute_uri(reverse("leaves:dashboard"))

    context = {
        "employee_name": employee.get_full_name() or employee.email,
        "leave_type": leave_request.leave_type.name,
        "dates": f"{leave_request.start_date:%d %b} - {leave_request.end_date:%d %b %Y}",  # noqa: E501
        "duration": leave_request.duration_days,
        "company_name": company.name,
        "dashboard_url": dashboard_url,
    }

    html_content = render_to_string("emails/new_request.html", context)
    text_content = (
        f"New leave request from {context['employee_name']}\n\n"
        f"Type: {context['leave_type']}\n"
        f"Dates: {context['dates']}\n"
        f"Duration: {context['duration']} day(s)\n\n"
        f"Review: {dashboard_url}"
    )

    for admin in admins:
        email = EmailMultiAlternatives(
            subject=f"New leave request from {context['employee_name']}",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()


def send_decision_email(leave_request, request):
    """Notify the employee of the approve/reject decision."""
    employee = leave_request.employee
    my_requests_url = request.build_absolute_uri(reverse("leaves:my_requests"))

    context = {
        "leave_type": leave_request.leave_type.name,
        "dates": f"{leave_request.start_date:%d %b} - {leave_request.end_date:%d %b %Y}",  # noqa: E501
        "duration": leave_request.duration_days,
        "status": leave_request.status,
        "comment": leave_request.reviewer_comment,
        "my_requests_url": my_requests_url,
    }

    html_content = render_to_string("emails/decision.html", context)

    if leave_request.status == "approved":
        subject = "Your leave request was approved"
        text_body = "Good news — your leave request has been approved."
    else:
        subject = "Your leave request was rejected"
        text_body = "Your leave request has been rejected."

    text_content = (
        f"{text_body}\n\n"
        f"Type: {context['leave_type']}\n"
        f"Dates: {context['dates']}\n"
        f"Duration: {context['duration']} day(s)\n"
    )
    if leave_request.reviewer_comment:
        text_content += f"\nComment: {leave_request.reviewer_comment}\n"

    text_content += f"\nView your requests: {my_requests_url}"

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[employee.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


def send_nudge_email(leave_request, request):
    employee = leave_request.employee
    company = employee.company
    admins = company.users.filter(role="admin")

    if not admins.exists():
        return

    dashboard_url = request.build_absolute_uri(reverse("leaves:dashboard"))
    waiting_days = (timezone.now().date() - leave_request.created_at.date()).days

    context = {
        "employee_name": employee.get_full_name() or employee.email,
        "leave_type": leave_request.leave_type.name,
        "dates": f"{leave_request.start_date:%d %b} - {leave_request.end_date:%d %b %Y}",  # noqa: E501
        "waiting_days": max(waiting_days, 0),
        "company_name": company.name,
        "dashboard_url": dashboard_url,
    }

    html_content = render_to_string("emails/nudge.html", context)
    text_content = (
        f"Reminder: {context['employee_name']} is waiting for a decision.\n\n"
        f"Type: {context['leave_type']}\n"
        f"Dates: {context['dates']}\n"
        f"Waiting: {context['waiting_days']} day(s)\n\n"
        f"Review: {dashboard_url}"
    )

    for admin in admins:
        email = EmailMultiAlternatives(
            subject=f"Reminder: pending leave request from {context['employee_name']}",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
