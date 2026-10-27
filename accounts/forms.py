from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Company, User


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "amara@operations.co",
                "autocomplete": "email",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "••••••••",
                "autocomplete": "current-password",
            }
        ),
    )


class AdminSignUpForm(UserCreationForm):
    full_name = forms.CharField(label="Full name", max_length=150)
    email = forms.EmailField(label="Work email")
    company_name = forms.CharField(label="Company name", max_length=150)

    class Meta:
        model = User
        fields = ("email", "full_name", "company_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({"placeholder": "ngozi@operations.co"})
        self.fields["full_name"].widget.attrs.update({"placeholder": "Ngozi"})
        self.fields["password1"].widget.attrs.update({"placeholder": "••••••••"})
        self.fields["password2"].widget.attrs.update({"placeholder": "••••••••"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]

        full_name = self.cleaned_data["full_name"].strip()
        parts = full_name.split(maxsplit=1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ""
        user.role = User.Role.ADMIN

        if commit:
            company = Company.objects.create(name=self.cleaned_data["company_name"])
            user.company = company
            user.save()
            super().save()

        return user


class InviteEmployeeForm(forms.Form):
    email = forms.EmailField(
        label="Work email",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "amara@operations.co",
            }
        ),
    )


class AcceptInviteForm(forms.Form):
    password1 = forms.CharField(
        label="Set a password",
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••"}),
        min_length=8,
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned_data
