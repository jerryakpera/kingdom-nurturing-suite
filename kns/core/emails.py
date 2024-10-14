"""
Emails functions for the `core` app.
"""

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone


def send_group_change_notification_email(
    request,
    profile,
    current_group,
    target_group,
    recipient,
):
    """
    Send a group change notification email to a recipient.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    profile : Profile
        The profile being moved to the new group.
    current_group : Group
        The profile's current group.
    target_group : Group
        The profile's new target group.
    recipient : Profile
        The profile that will receive the email notification.
    """
    subject = f"{profile.get_full_name()} has changed groups"

    # Get the current domain
    current_site = get_current_site(request)

    # Render the HTML email template
    html_message = render_to_string(
        "core/emails/change_group_notification_email.html",
        {
            "recipient": recipient,
            "profile": profile,
            "current_group": current_group,
            "target_group": target_group,
            "domain": current_site.domain,
            "current_year": timezone.now().year,
        },
    )

    # Send the email
    send_mail(
        subject=subject,
        message="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient.email],
        html_message=html_message,
    )
