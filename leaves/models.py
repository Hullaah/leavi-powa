from django.conf import settings
from django.db import models


class LeaveType(models.Model):
    """
    Global leave types (Annual, Sick, Casual, Unpaid, Study).
    We keep them global for simplicity. Companies control how many days
    they give via LeaveEntitlement.
    """

    class Code(models.TextChoices):
        ANNUAL = "annual", "Annual"
        SICK = "sick", "Sick"
        CASUAL = "casual", "Casual"
        UNPAID = "unpaid", "Unpaid"
        STUDY = "study", "Study"

    code = models.CharField(max_length=20, choices=Code.choices, unique=True)
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, blank=True)  # for UI chips later

    class Meta:
        ordering = ["name"]  # noqa: RUF012

    def __str__(self):
        return self.name


class LeaveEntitlement(models.Model):
    """
    How many days of a particular leave type a company grants per year.
    """

    company = models.ForeignKey(
        "accounts.Company", on_delete=models.CASCADE, related_name="leave_entitlements"
    )
    leave_type = models.ForeignKey(
        LeaveType, on_delete=models.CASCADE, related_name="entitlements"
    )
    days_per_year = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ("company", "leave_type")
        verbose_name_plural = "leave entitlements"

    def __str__(self):
        return f"{self.company} - {self.leave_type}: {self.days_per_year} days"


class LeaveRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leave_requests",
    )
    leave_type = models.ForeignKey(
        LeaveType, on_delete=models.PROTECT, related_name="requests"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(max_length=500, blank=True)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_requests",
    )
    reviewer_comment = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    # Nudge tracking
    nudge_count = models.PositiveSmallIntegerField(default=0)
    last_nudged_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]  # noqa: RUF012

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})"  # noqa: E501

    @property
    def is_pending(self):
        return self.status == self.Status.PENDING

    @property
    def duration_days(self):
        """Simple inclusive day count. We can later make this working-days only."""
        return (self.end_date - self.start_date).days + 1
