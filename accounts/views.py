from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import AdminSignUpForm, LoginForm


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class AdminSignUpView(CreateView):
    form_class = AdminSignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")
