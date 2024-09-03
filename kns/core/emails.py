"""
Email functions for the core app.

This module contains functions related to sending email notifications
for various actions, such as approving a member's request to become a leader.
"""

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from kns.accounts.utils import generate_verification_token


def send_make_leader_action_approval_consumer_email(
    request,
    member,
    requester,
    consumer,
):  # pragma: no cover
    """
    Send an email to a consumer (e.g., an admin or leader) requesting
    approval to make a specified member a leader.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object, used to retrieve the current site domain.
    member : Profile
        The profile object of the member to be approved for a leader role.
    requester : Profile
        The profile object of the user requesting the approval.
    consumer : Profile
        The profile object of the consumer who will receive the approval
        request email.

    Returns
    -------
    None
        The function sends an email and updates the consumer's profile but does
        not return any value.
    """
    subject = f"Approval request to make {member.get_full_name()} a leader role."

    # Get the current domain
    current_site = get_current_site(request)

    # Generate a UID and token for the consumer
    uid = urlsafe_base64_encode(force_bytes(consumer.user.pk))
    token = generate_verification_token(consumer.user)

    # Get the protocol depending on the environment
    protocol = "https" if not settings.DEBUG else "http"

    # Render the HTML email template
    html_message = render_to_string(
        "core/emails/mlaa_consumer.html",
        {
            "member": member,
            "requester": requester,
            "consumer": consumer,
            "domain": current_site.domain,
            "uid": uid,
            "token": token,
            "protocol": protocol,
        },
    )

    # Send the email
    send_mail(
        subject=subject,
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[consumer.email],
        html_message=html_message,
    )

    # Save the token to the consumer's profile (if you are storing it)
    consumer.email_token = token
    consumer.save()
