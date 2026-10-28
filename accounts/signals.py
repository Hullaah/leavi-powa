from django.db.models.signals import post_save
from django.dispatch import receiver

from leaves.models import LeaveEntitlement, LeaveType

from .models import Company

DEFAULT_ENTITLEMENTS = {
    "annual": 20,
    "sick": 10,
    "casual": 5,
    "study": 5,
    "unpaid": 0,  # 0 usually means “unlimited” or “no fixed entitlement”
}


@receiver(post_save, sender=Company)
def create_default_entitlements(sender, instance, created, **kwargs):
    if not created:
        return

    for code, days in DEFAULT_ENTITLEMENTS.items():
        try:
            leave_type = LeaveType.objects.get(code=code)
            LeaveEntitlement.objects.get_or_create(
                company=instance,
                leave_type=leave_type,
                defaults={"days_per_year": days},
            )
        except LeaveType.DoesNotExist:
            continue
