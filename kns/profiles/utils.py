"""
Util functions for the `profiles` app.
"""

from datetime import timedelta

from django.urls import resolve
from django.utils import timezone

from kns.groups.models import Group, GroupMember

from .models import EncryptionReason, Profile


def get_profile_slug(request):
    """
    Extract the profile slug from the given HTTP request.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object from which to extract the profile slug.

    Returns
    -------
    str
        The profile slug if found, otherwise an empty string.
    """
    slug = ""

    if request.path.startswith("/profiles/"):
        match = resolve(request.path_info)
        # Extract the slug from the request path, default to an empty string if not found
        slug = match.kwargs.get("profile_slug", "")

    return slug


def calculate_max_dob(age):
    """
    Calculate the maximum date of birth based on the provided age.

    Parameters
    ----------
    age : int
        The age of the person for whom the maximum date of birth is being
        calculated.

    Returns
    -------
    str
        The maximum date of birth formatted as a string in the format
        "YYYY-MM-DD".
    """
    current_date = timezone.now().date()
    max_dob = current_date - timedelta(days=(age * 365))

    formatted_max_dob = max_dob.strftime("%Y-%m-%d")

    return formatted_max_dob


def name_with_apostrophe(name):
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


def populate_encryption_reasons(encryption_reasons_data):
    """
    Populate the database with encryption reasons data.

    This function iterates over a list of encryption reasons data and
    creates `EncryptionReason` objects in the database.

    Parameters
    ----------
    encryption_reasons_data : list
        A list of dictionaries where each dictionary contains the 'title'.
    """

    for encryption_reason_data in encryption_reasons_data:
        encryption_reason_exists = EncryptionReason.objects.filter(
            title=encryption_reason_data["title"],
        ).exists()

        if not encryption_reason_exists:
            EncryptionReason.objects.create(
                title=encryption_reason_data["title"],
                description=encryption_reason_data["description"],
                author=Profile.objects.first(),
            )


def is_profiles_group_leader(user, profile):
    """
    Determine if the given user is the leader of the group to which the specified profile belongs.

    Parameters
    ----------
    user : User
        The user whose leadership status is being checked.
    profile : Profile
        The profile to be checked against the user's leadership.

    Returns
    -------
    bool
        `True` if the user is the leader of the profile's group, `False` otherwise.
    """
    users_group_exists = Group.objects.filter(leader=user.profile).exists()

    if not users_group_exists:
        return False

    # If profile is the leader of their own group
    if not hasattr(profile, "group_in") and user.profile == profile:
        return True

    # If the profile is not in any group, return False
    if not hasattr(profile, "group_in"):
        return False

    profile_group_member_exists = GroupMember.objects.filter(
        profile=profile,
        group=user.profile.group_led,
    ).exists()

    # Check if the user's profile is the leader of the group the profile belongs to
    if user.profile == profile.group_in.group.leader:
        return True

    return profile_group_member_exists
