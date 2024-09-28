"""
Utility functions for sending emails related to user account management.
"""

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from kns.accounts.utils import generate_verification_token


def send_new_leader_email(request, profile, profiles_leader):
    """
    Send an email to a user notifying them of their new role as a leader on KNS.
    The email includes a link for the user to set their password if needed.

    The email contains a UID and token for verifying the user, and provides the
    current site's domain for generating the URL in the email. The email is
    rendered from an HTML template.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object, used to retrieve the current site domain.
    profile : Profile
        The profile object of the user who has been assigned a new leader role.
    profiles_leader : Profile
        The profile of the user assigning the leader role, included in the email
        as the current leader.

    Returns
    -------
    None
        This function sends an email to the user and updates the profile's
        `email_token` with a generated verification token, but does not return a value.
    """
    subject = "You are now a leader on KNS"

    # Get the current domain
    current_site = get_current_site(request)

    # Generate a UID and token for the profile
    uid = urlsafe_base64_encode(force_bytes(profile.pk))
    token = generate_verification_token(profile.user)

    # Render the HTML email template
    html_message = render_to_string(
        "profiles/emails/new_leader_email.html",
        {
            "profile": profile,
            "domain": current_site.domain,
            "uid": uid,
            "token": token,
            "profiles_leader": profiles_leader,
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


def send_new_member_email(request, profile, profiles_leader):
    """
    Send an email to a user notifying them that their role has been
    changed to `member` on KNS.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object, used to retrieve the current site domain.
    profile : Profile
        The profile object of the user who has been assigned a new leader role.
    profiles_leader : Profile
        The profile of the user assigning the leader role, included in the email
        as the current leader.

    Returns
    -------
    None
        This function sends an email to the user and updates the profile's
        `email_token` with a generated verification token, but does not return a value.
    """
    subject = "You are now a member role on KNS"

    # Get the current domain
    current_site = get_current_site(request)

    # Render the HTML email template
    html_message = render_to_string(
        "profiles/emails/new_member_email.html",
        {
            "profile": profile,
            "domain": current_site.domain,
            "profiles_leader": profiles_leader,
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


def send_new_external_person_email(request, profile, profiles_leader):
    """
    Send an email to a user notifying them that their role has been
    changed to `external_person` on KNS.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object, used to retrieve the current site domain.
    profile : Profile
        The profile object of the user who has been assigned a new leader role.
    profiles_leader : Profile
        The profile of the user assigning the leader role, included in the email
        as the current leader.

    Returns
    -------
    None
        This function sends an email to the user and updates the profile's
        `email_token` with a generated verification token, but does not return a value.
    """
    subject = "You are now an external person role on KNS"

    # Get the current domain
    current_site = get_current_site(request)

    # Render the HTML email template
    html_message = render_to_string(
        "profiles/emails/new_external_person_email.html",
        {
            "profile": profile,
            "domain": current_site.domain,
            "profiles_leader": profiles_leader,
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
