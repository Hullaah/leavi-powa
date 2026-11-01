from django.urls import path

from . import views

app_name = "leaves"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("my-requests/", views.my_requests, name="my_requests"),
    path("new/", views.NewLeaveRequestView.as_view(), name="new_request"),
    path("approve/<int:pk>/", views.approve_request, name="approve_request"),
    path("reject/<int:pk>/", views.reject_request, name="reject_request"),
    path("all/", views.all_requests, name="all_requests"),
    path("nudge/<int:pk>/", views.nudge_request, name="nudge_request"),
]
