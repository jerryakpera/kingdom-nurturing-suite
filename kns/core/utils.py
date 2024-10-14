"""
Util functions for the `core` app.
"""

from .models import Notification, NotificationRecipient


def log_this(item, sign="*"):  # pragma: no cover
    """
    Log an item with a specified visual separator.

    Parameters
    ----------
    item : str
        The item or message to be logged.
    sign : str, optional
        The character used to create the separator lines. Defaults to '*'.

    Returns
    -------
    None
        This function does not return a value. It prints the item and separator to the console.
    """

    print("")
    print(sign * 30)
    print(item)
    print(sign * 30)
    print("")


def create_group_change_notification(profile, current_group, target_group):
    """
    Create a notification for a group change event.

    This function generates a notification indicating that a profile has
    been moved from one group to another. It includes details about the
    profile, the current group, and the target group.

    Parameters
    ----------
    profile : Profile
        The profile of the user being moved between groups.
    current_group : Group
        The group from which the profile is being moved.
    target_group : Group
        The group to which the profile is being moved.

    Returns
    -------
    Notification
        The created Notification instance representing the group change.
    """
    notification = Notification.objects.create(
        sender=current_group.leader,
        notification_type="group_move",
        title="Change of group",
        message=(
            f"{profile.get_full_name()} has been successfully moved from "
            f"{current_group.name} to {target_group.name}. Click the link to view."
        ),
        link=target_group.get_members_url(),
    )

    return notification
