from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


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
    first_name = forms.CharField(label="Full name", max_length=150)
    email = forms.EmailField(label="Work email")

    class Meta:
        model = User
        fields = ("first_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make username = email
        self.fields["email"].widget.attrs.update({"placeholder": "ngozi@operations.co"})
        self.fields["first_name"].widget.attrs.update({"placeholder": "Ngozi Adeyemi"})
        self.fields["password1"].widget.attrs.update({"placeholder": "••••••••"})
        self.fields["password2"].widget.attrs.update({"placeholder": "••••••••"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.role = User.Role.ADMIN
        if commit:
            user.save()
        return user
