from django.urls import path

from . import views

app_name = "leaves"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("my-requests/", views.my_requests, name="my_requests"),
]
