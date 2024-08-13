import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .emails import send_password_change_email
from .forms import ChangePasswordForm, LoginForm
from .utils import is_safe_url

# Configure logging
logger = logging.getLogger(__name__)


@login_required
def index(request):
    return render(
        request=request,
        template_name="accounts/pages/index.html",
        context={},
    )


def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")

        user = authenticate(email=email, password=password)

        if user is not None:
            login(request, user)

            # Redirect to the URL where the user
            # intended to go or the default index page
            next_url = request.POST.get("next", "accounts:index")

            if is_safe_url(next_url, allowed_hosts=request.get_host()):
                return redirect(next_url)
            else:
                return redirect("accounts:index")
        else:
            form.add_error(None, "Incorrect email or password. Please try again.")
            # Log the failed attempt for debugging purposes
            logger.warning(f"Failed login attempt for email: {email}")

    context = {
        "login_form": form,
    }

    return render(
        request=request,
        template_name="accounts/pages/login.html",
        context=context,
    )


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@login_required
def change_password(request):
    if request.method == "POST":
        change_password_form = ChangePasswordForm(request.POST)

        if change_password_form.is_valid():
            current_password = change_password_form.cleaned_data["current_password"]
            new_password = change_password_form.cleaned_data["new_password"]

            # Authenticate the user with the current password
            user = authenticate(email=request.user.email, password=current_password)

            if user is None:
                # Provide error feedback for incorrect current password
                change_password_form.add_error(
                    "current_password",
                    "You entered an incorrect password",
                )
            else:
                # Update the user's password and re-authenticate
                user.set_password(new_password)
                user.save()
                login(request, user)

                # Send email notification
                send_password_change_email(user.email)

                # Provide success feedback
                messages.success(
                    request,
                    "Your password has been updated",
                )
                return redirect("accounts:index")

    else:
        change_password_form = ChangePasswordForm()

    context = {
        "change_password_form": change_password_form,
    }

    return render(
        request=request,
        template_name="accounts/pages/change-password.html",
        context=context,
    )
