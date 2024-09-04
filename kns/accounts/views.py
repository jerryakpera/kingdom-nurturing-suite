"""
Views for handling user authentication and account management.

This module includes views for user login, logout, password change, and
the user dashboard. It also handles form submissions, user authentication,
password changes, and related email notifications.
"""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from kns.custom_user.models import User

from .decorators import guest_required
from .emails import send_password_change_email, send_verification_email
from .forms import ChangePasswordForm, LoginForm, SetPasswordForm
from .utils import decode_uid, verify_token


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

    context = {
        "user": request.user,
    }

    return render(
        request=request,
        template_name="accounts/pages/index.html",
        context=context,
    )


@guest_required
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

        # Authenticate the user first
        user = authenticate(
            email=email,
            password=password,
        )

        if user is not None:
            # Now that user is authenticated, check if they are a superuser or a leader
            if not user.is_superuser and user.profile.role != "leader":
                form.add_error(
                    None,
                    "Access denied. You do not have the necessary permissions.",
                )

                context = {
                    "login_form": form,
                }

                return render(
                    request=request,
                    template_name="accounts/pages/login.html",
                    context=context,
                )
            else:
                # Log the user in
                login(request, user)

                return redirect("accounts:index")
        else:
            form.add_error(
                None,
                "Incorrect email or password. Please try again.",
            )

    context = {
        "login_form": form,
    }

    return render(
        request=request,
        template_name="accounts/pages/login.html",
        context=context,
    )


@login_required
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
        template_name="accounts/pages/change_password.html",
        context=context,
    )


def verify_email(request, uidb64, token):
    """
    Verify the user's email address.

    Decodes the user ID from the URL and validates the provided token.
    If valid, updates     the user's verification status and redirects
    to the home page. Otherwise, an error message is displayed, and
    the user is redirected to a failure page.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object containing the verification link.
    uidb64 : str
        The encoded user ID from the URL.
    token : str
        The token used to verify the email address.

    Returns
    -------
    HttpResponse
        A redirect response to the home page or a rendered template for
        verification failure.
    """
    uid = decode_uid(uidb64)
    user = get_object_or_404(User, pk=uid)

    if user and verify_token(user, token):
        user.verified = True
        user.save()

        messages.success(
            request,
            "Your email has been verified successfully!",
        )

        return redirect("core:index")
    else:
        messages.error(
            request,
            "The verification link is invalid or has expired.",
        )

        return render(
            request,
            "accounts/pages/verification_failed.html",
        )


@login_required
def verification_email(request, user_id):
    """
    View to send a verification email to the user's email address.

    This view retrieves the user by their ID, generates a verification link,
    and sends it to the user's registered email address. A success or error
    message is displayed based on the outcome.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    user_id : str
        The ID of the user to whom the verification email will be sent.

    Returns
    -------
    HttpResponseRedirect
        Redirects to a relevant page, typically the user's profile or dashboard,
        with a success or error message.
    """

    # Fetch the user by ID, or return a 404 if not found
    user = get_object_or_404(User, pk=user_id)

    # TODO: Work on permissions for this view

    # Send the verification email
    try:
        send_verification_email(request, user)
        messages.success(
            request,
            "Verification email sent successfully.",
        )

    except Exception as e:
        messages.error(
            request,
            f"Failed to send verification email: {str(e)}",
        )

    # Redirect to a relevant page (e.g., user profile or dashboard)
    return redirect(user.profile)


@login_required
def agree_to_terms(request):
    """
    View to agree to terms.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponseRedirect
        Redirects to a relevant page, typically the user's profile or dashboard,
        with a success or error message.
    """

    if request.user.agreed_to_terms:
        messages.success(
            request,
            "You have already agreed to the Terms and Conditions.",
        )

        return redirect(
            request.user.profile.get_absolute_url(),
        )

    if request.method == "POST":
        # Check if the form is submitted and the checkbox is checked
        if "agree_checkbox" in request.POST:
            # User agreed to the terms, handle the logic here
            request.user.agreed_to_terms = True
            request.user.save()

            # Set a success message
            messages.success(
                request,
                "You have successfully agreed to the Terms and Conditions.",
            )

            return redirect(
                request.user.profile.get_absolute_url(),
            )

        # If the checkbox is not checked, set an error message
        messages.error(
            request,
            "You must agree to the Terms and Conditions to proceed.",
        )

    # Render the template with the form
    return render(
        request=request,
        template_name="accounts/pages/agree_to_terms.html",
    )


def set_password(request, uidb64, token):
    """
    Handle the process of setting a new password for the user.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object used to process the request.
    uidb64 : str
        The base64 encoded user ID.
    token : str
        The token generated to verify the user.

    Returns
    -------
    HttpResponse
        Renders the set password form or redirects with a
        success or error message.
    """

    set_password_form = SetPasswordForm(request.POST or None)

    uid = decode_uid(uidb64)
    user = get_object_or_404(User, pk=uid)

    profile = user.profile

    # Check if the user already has a password set
    if user.has_usable_password() and user.password:
        messages.info(
            request=request,
            message=(
                "You already have a password set. "
                "Please log in using your existing password."
            ),
        )

        return redirect("accounts:login")

    if user and verify_token(user, token):
        if request.method == "POST":
            if set_password_form.is_valid():
                new_password = set_password_form.cleaned_data.get(
                    "new_password",
                )

                user = User.objects.get(
                    email=profile.email,
                )

                user.set_password(new_password)
                user.save()

                profile.save()

                messages.success(
                    request,
                    (
                        "Your password has been set. Use your newly set "
                        "password to login to KNT"
                    ),
                )

                return redirect("accounts:login")
            else:
                # Extract form errors and create a user-friendly message
                errors = set_password_form.errors.as_text()

                messages.error(request, f"Password reset failed. {errors}")

        context = {
            "token": token,
            "uidb64": uidb64,
            "set_password_form": set_password_form,
        }

        return render(
            request=request,
            template_name="accounts/pages/set_password.html",
            context=context,
        )

    else:
        messages.warning(
            request=request,
            message=(
                "The link you are using has expired."
                "Please request a new link from your leader."
            ),
        )

        context = {
            "token": token,
            "uidb64": uidb64,
            "set_password_form": set_password_form,
        }

        return render(
            request=request,
            template_name="accounts/pages/set_password.html",
            context=context,
        )
