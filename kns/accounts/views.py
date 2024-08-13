"""
Views for handling user authentication and account management.

This module includes views for user login, logout, password change, and
the user dashboard. It also handles form submissions, user authentication,
password changes, and related email notifications.
"""

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
    """
    Render the user dashboard page.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        The rendered template for the user dashboard.
    """
    return render(
        request=request,
        template_name="accounts/pages/index.html",
        context={},
    )


def login_view(request):
    """
    Handle user login.

    Renders the login form and processes user authentication. On successful
    login, the user is redirected to the intended URL or the default dashboard
    page. On failure, an error message is shown.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        The rendered template for the login page or a redirect response.
    """
    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")

        user = authenticate(email=email, password=password)

        if user is not None:
            login(request, user)

            # Redirect to the URL where the user intended to go or the default index page
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
    """
    Handle user logout.

    Logs out the user and redirects to the login page.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        A redirect response to the login page.
    """
    logout(request)
    return redirect("accounts:login")


@login_required
def change_password(request):
    """
    Handle password change for the logged-in user.

    Renders the password change form and processes the password update. If the
    current password is correct and the new passwords match, the user's password
    is updated, the user is re-authenticated, and a notification email is sent.
    On success, the user is redirected to the dashboard page. On failure, an error
    message is shown.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        The rendered template for the password change page or a redirect response.
    """
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
