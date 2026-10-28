from django import forms

from .models import LeaveRequest, LeaveType


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["leave_type", "start_date", "end_date", "reason"]  # noqa: RUF012
        widgets = {  # noqa: RUF012
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Briefly describe the reason for your leave",
                    "maxlength": 500,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Only show leave types that the company has entitlements for
        if self.user and self.user.company:
            allowed_types = LeaveType.objects.filter(
                entitlements__company=self.user.company
            ).distinct()
            self.fields["leave_type"].queryset = allowed_types

        self.fields["leave_type"].label = "Leave type"
        self.fields["start_date"].label = "Start date"
        self.fields["end_date"].label = "End date"
        self.fields["reason"].label = "Reason"

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")

        if start and end and end < start:
            self.add_error("end_date", "End date cannot be before start date.")

        return cleaned_data
