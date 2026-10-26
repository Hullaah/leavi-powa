from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import AdminSignUpForm, InviteEmployeeForm, LoginForm
from .models import Invitation, User


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


@login_required
def invite_employee(request):
    if not request.user.is_admin:
        return redirect("dashboard")

    if request.method == "POST":
        form = InviteEmployeeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]

            # Prevent inviting existing users
            if User.objects.filter(email=email).exists():
                messages.error(request, "A user with this email already exists.")
            else:
                invitation = Invitation.objects.create(
                    email=email, invited_by=request.user
                )

                # Build acceptance link
                accept_url = request.build_absolute_uri(
                    f"/accounts/accept-invite/{invitation.token}/"
                )

                context = {
                    "inviter_name": request.user.get_full_name()
                    or request.user.username,
                    "accept_url": accept_url,
                    "company_name": request.user.company.name,
                }

                html_content = render_to_string("emails/invitation.html", context)
                text_content = f"""You're invited to join leavi

                {context["inviter_name"]} has invited you to join leavi.

                Accept your invitation and set your password:
                {accept_url}

                This invitation expires in 7 days.
                """

                email = EmailMultiAlternatives(
                    subject="You're invited to join leavi",
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send()

                messages.success(request, f"Invitation sent to {' '.join(email.to)}")
                return redirect("accounts:invite")
    else:
        form = InviteEmployeeForm()

    invitations = Invitation.objects.filter(invited_by=request.user)[:20]

    return render(
        request,
        "accounts/invite.html",
        {
            "form": form,
            "invitations": invitations,
        },
    )
