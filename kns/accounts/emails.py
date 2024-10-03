"""
Utility functions for sending emails related to user account management.
"""

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .utils import generate_verification_token


def send_password_change_email(user_email):
    """
    Send an email notification when a user's password is changed.

    Parameters
    ----------
    user_email : str
        The email address of the user who changed their password.
    """
    subject = "Password Changed Successfully"

    message = (
        "Dear User,\n\n"
        "Your password has been successfully changed.\n\n"
        "If you did not make this change, please contact support immediately."
    )

    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
    )


def send_verification_email(request, user):
    """
    Send a verification email to the user.

    This function generates a unique token and a UID for the user,
    constructs a verification link, and sends an HTML email to the user's
    registered email address with a link to verify their account. The token
    is also saved to the user's profile for later validation.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object, used to retrieve the current site domain.
    user : User
        The user object to whom the verification email is being sent.

    Returns
    -------
    None
        The function sends an email and updates the user's profile but does
        not return any value.
    """
    subject = "Verify your email address"

    # Get the current domain
    current_site = get_current_site(request)

    # Generate a UID and token for the user
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = generate_verification_token(user)

    # Render the HTML email template
    html_message = render_to_string(
        "accounts/emails/verification_email.html",
        {
            "user": user,
            "domain": current_site.domain,
            "uid": uid,
            "token": token,
        },
    )

    # Send the email
    send_mail(
        subject=subject,
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
    )

    # Save the token to the user's profile (if you are storing it)
    user.profile.save_email_token(token)


def send_set_password_email(request, profile):
    """
    Send an email to the user to set their password.

    This function generates a unique token and UID for the profile,
    constructs a set password link, and sends an HTML email to the profile's
    registered email address. The token is also saved to the profile for
    later validation.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object, used to retrieve the current site domain.
    profile : Profile
        The profile object of the user who needs to set a password.

    Returns
    -------
    None
        The function sends an email and updates the profile but does
        not return any value.
    """
    subject = "Set your KNS password"

    # Get the current domain
    current_site = get_current_site(request)

    # Generate a UID and token for the profile
    uid = urlsafe_base64_encode(force_bytes(profile.pk))
    token = generate_verification_token(profile.user)

    # Render the HTML email template
    html_message = render_to_string(
        "accounts/emails/set_password_email.html",
        {
            "profile": profile,
            "domain": current_site.domain,
            "uid": uid,
            "token": token,
        },
    )

    # Send the email
    send_mail(
        subject=subject,
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[profile.email],
        html_message=html_message,
    )

    # Save the token to the profile
    profile.save_email_token(token)


def send_welcome_email(request, profile, leader):
    """
    Send a welcome email to a newly registered profile.

    This function generates a unique token and UID for the profile,
    constructs a verification link, and sends an HTML email to the profile's
    registered email address. The token is also saved to the profile for
    later validation.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object, used to retrieve the current site domain.
    profile : Profile
        The profile object of the user who has registered.
    leader : User
        The leader who initiated the profile creation.
    """
    subject = "Verify your email address"

    # Get the current domain
    current_site = get_current_site(request)

    # Generate a UID and token for the profile
    uid = urlsafe_base64_encode(force_bytes(profile.pk))
    token = generate_verification_token(profile.user)

    # Render the HTML email template
    html_message = render_to_string(
        "accounts/emails/welcome_email.html",
        {
            "profile": profile,
            "leader": leader,
            "domain": current_site.domain,
            "uid": uid,
            "token": token,
        },
    )

    # Send the email
    send_mail(
        subject=subject,
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[profile.email],
        html_message=html_message,
    )

    # Save the token to the profile
    profile.email_token = token
    profile.save()
