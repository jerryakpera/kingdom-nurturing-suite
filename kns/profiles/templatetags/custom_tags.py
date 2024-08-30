"""
Custom tags for the `profiles` app.
"""

from django import template

from kns.core.utils import log_this

register = template.Library()


@register.filter
def get_nth_element(lst, index):
    """
    Return the element at the specified index from the given list.

    This custom template filter retrieves the element at the `index` position from the `lst`.
    If the index is out of range, not a valid integer, or if the list is `None`, it returns `None`.

    Parameters
    ----------
    lst : list
        The list from which the element is to be retrieved.
    index : int or str
        The index of the element to retrieve. This can be provided as an integer or a string
        that can be converted to an integer.

    Returns
    -------
    object or None
        The element at the specified index, or `None` if the index is invalid or the list is empty.
    """
    try:
        if index is None:
            return None
        return lst[int(index)]
    except (IndexError, ValueError, TypeError):
        return None


@register.filter
def can_edit_profile(user, profile):
    """
    Determine if the given user can edit the specified profile.

    This custom template filter checks if the `user` has the permission to edit the `profile`.
    The user can edit the profile if:
    - The profile belongs to the user.
    - The profile does not belong to a leader with a usable password.
    - The user is a member of the group led by the profile's group.

    Parameters
    ----------
    user : User
        The user whose permissions are being checked.
    profile : Profile
        The profile to be checked for edit permissions.

    Returns
    -------
    bool
        `True` if the user can edit the profile, `False` otherwise.
    """
    if profile == user.profile:
        return True

    if (
        profile.role == "leader"
        and profile.user.has_usable_password
        and profile.user.password
    ):
        return False

    if not hasattr(user.profile, "group_led"):  # pragma: no cover
        return False

    return user.profile.group_led.is_member(profile)


@register.filter
def name_with_apostrophe(name: str):
    """
    Add an apostrophe to a name to form a possessive version.

    This function appends an apostrophe to the given name. If the name ends with
    an "s", it simply adds an apostrophe. Otherwise, it adds "'s" to the name.

    Parameters
    ----------
    name : str
        The name to which the possessive apostrophe is to be added.

    Returns
    -------
    str
        The name with an appended possessive apostrophe.
    """
    if name.strip() == "":
        return ""

    if name[-1] == "s":
        return name + "'"
    else:
        return name + "'s"
