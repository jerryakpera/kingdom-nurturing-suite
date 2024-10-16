"""
Context processors for the `core` app.
"""

from collections import defaultdict

from .models import NotificationRecipient, Setting


def settings_context(request):
    """
    Add settings to the context for all templates.

    Parameters
    ----------
    request : HttpRequest
        A HttpRequest object.

    Returns
    -------
    dict
        A dictionary with a 'settings' key containing the settings instance.
    """
    settings = Setting.get_or_create_setting()

    return {
        "settings": settings,
    }


def notifications_context(request):
    """
    Add unread notifications to the context for authenticated users.

    Retrieves unread notifications for the logged-in user and groups them
    by time period (e.g., Today, Yesterday).

    Parameters
    ----------
    request : HttpRequest
        A HttpRequest object.

    Returns
    -------
    dict
        A dictionary containing:
        - 'unread_notifications': a list of unread notifications.
        - 'grouped_notifications': a dictionary grouping notifications by time period.
    """
    if request.user.is_authenticated:
        # Get the unread notifications with related notification details
        unread_notifications = NotificationRecipient.objects.filter(
            recipient=request.user.profile,
            is_read=False,
        ).select_related("notification")[:10]

        # Group notifications by time period (Today, Yesterday, etc.)
        grouped_notifications = defaultdict(list)
        for recipient_notification in unread_notifications:
            notification = recipient_notification.notification
            period = notification.time_period()  # Use the time_period method
            grouped_notifications[period].append(notification)

        # Convert defaultdict to a regular dict before passing to the template
        grouped_notifications = dict(grouped_notifications)
    else:
        unread_notifications = []
        grouped_notifications = {}

    return {
        "unread_notifications": unread_notifications,
        "grouped_notifications": grouped_notifications,
    }
