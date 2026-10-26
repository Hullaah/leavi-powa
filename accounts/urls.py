from django.urls import path

from .views import AdminSignUpView, CustomLoginView, CustomLogoutView, invite_employee

app_name = "accounts"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("signup/", AdminSignUpView.as_view(), name="signup"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("invite/", invite_employee, name="invite"),
]
