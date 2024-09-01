"""
Custom tags for the `groups` app.
"""

from django import template

from kns.groups.models import Group

register = template.Library()


@register.filter
def is_leader_of_parent_group(user, group):
    """
    Check if the user is the leader of the parent group of the given group.

    Parameters
    ----------
    user : User
        The user whose profile will be checked.
    group : Group
        The group whose parent group will be checked.

    Returns
    -------
    bool
        True if the user is the leader of the parent group, False otherwise.
    """
    if not hasattr(user, "profile") or not user.profile:
        return False

    # Get the parent group of the provided group
    parent_group = group.parent

    # Check if the group has a parent
    if not parent_group:
        if group.leader == user.profile:
            return True
        else:
            return False

    # Check if the user's profile is the leader of the parent group
    return parent_group.leader == user.profile
