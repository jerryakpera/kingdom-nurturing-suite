"""
This module contains utility methods for managing and interacting with Profile objects.

Methods
-------
get_full_name(profile):
    Return the full name of the profile instance.

is_leading_group(profile):
    Return if the profile instance is a leader of a group.

get_absolute_url(profile):
    Return the absolute URL to access a detail view of this profile.

get_involvements_url(profile):
    Return the involvements URL to access a detail view of this profile.

get_trainings_url(profile):
    Return the trainings URL to access a detail view of this profile.

get_activities_url(profile):
    Return the activities URL to access a detail view of this profile.

get_settings_url(profile):
    Return the settings URL to access a detail view of this profile.

get_role_display_str(profile):
    Return the string display for this profile role.

is_eligible_to_register_group(profile):
    Determine if the user is eligible to register a new group.

is_profile_complete(profile):
    Check if the user's profile is fully completed.
"""

from django.urls import reverse


def get_full_name(profile):
    """
    Return the full name of the profile instance.

    Parameters
    ----------
    profile : Profile
        The profile instance.

    Returns
    -------
    str
        Full name of the profile instance.
    """
    return f"{profile.first_name} {profile.last_name}"


def is_leading_group(profile):
    """
    Return if the profile instance is a leader of a group.

    Parameters
    ----------
    profile : Profile
        The profile instance.

    Returns
    -------
    bool
        True if the profile is leading a group, False otherwise.
    """
    return hasattr(profile, "group_led")


def get_absolute_url(profile):
    """
    Return the absolute URL to access a detail view of this profile.

    Parameters
    ----------
    profile : Profile
        The profile instance.

    Returns
    -------
    str
        The absolute URL of the profile's detail view.
    """
    return reverse(
        "profiles:profile_detail",
        kwargs={
            "profile_slug": profile.slug,
        },
    )


def get_involvements_url(profile):
    """
    Return the involvements URL to access a detail view of this profile.

    Parameters
    ----------
    profile : Profile
        The profile instance.

    Returns
    -------
    str
        The involvements URL of the profile's detail view.
    """
    return reverse(
        "profiles:profile_involvements",
        kwargs={
            "profile_slug": profile.slug,
        },
    )


def get_trainings_url(profile):
    """
    Return the trainings URL to access a detail view of this profile.

    Parameters
    ----------
    profile : Profile
        The profile instance.

    Returns
    -------
    str
        The trainings URL of the profile's detail view.
    """
    return reverse(
        "profiles:profile_trainings",
        kwargs={
            "profile_slug": profile.slug,
        },
    )


def get_activities_url(profile):
    """
    Return the activities URL to access a detail view of this profile.

    Parameters
    ----------
    profile : Profile
        The profile instance.

    Returns
    -------
    str
        The activities URL of the profile's detail view.
    """
    return reverse(
        "profiles:profile_activities",
        kwargs={
            "profile_slug": profile.slug,
        },
    )


def get_settings_url(profile):
    """
    Return the settings URL to access a detail view of this profile.

    Parameters
    ----------
    profile : Profile
        The profile instance.

    Returns
    -------
    str
        The settings URL of the profile's detail view.
    """
    return reverse(
        "profiles:profile_settings",
        kwargs={
            "profile_slug": profile.slug,
        },
    )


def get_role_display_str(profile):
    """
    Return the string display for this profile role.

    Parameters
    ----------
    profile : Profile
        The profile instance.

    Returns
    -------
    str
        The string representation of the profile's role.
    """
    if profile.role in ["leader", "member"]:
        return profile.role.title()

    return "External Person"


def is_eligible_to_register_group(profile):
    """
    Determine if the user is eligible to register a new group.

    Parameters
    ----------
    profile : Profile
        The profile instance.

    Returns
    -------
    bool
        True if the user meets all eligibility criteria, otherwise False.
    """
    # Check if user is a leader of an existing group
    if hasattr(profile, "group_led"):
        return False

    # Check if user has the leader role
    if profile.role != "leader":
        return False

    # Check if email is verified
    if not profile.user.verified:
        return False

    # Check if user has agreed to terms
    if not profile.user.agreed_to_terms:
        return False

    # Check if user is a visitor
    if profile.user.is_visitor:
        return False

    # Check if the profile is fully completed
    if not profile.is_profile_complete():
        return False

    return True


def is_profile_complete(profile):
    """
    Check if the user's profile is fully completed.

    Parameters
    ----------
    profile : Profile
        The profile instance.

    Returns
    -------
    bool
        True if all required fields are filled out and additional
        criteria are met, otherwise False.
    """
    required_fields = [
        profile.first_name,
        profile.last_name,
        profile.gender,
        profile.date_of_birth,
        profile.location_country,
        profile.location_city,
        profile.role,
    ]

    # Ensure all required fields are filled out
    if not all(required_fields):
        return False

    # Ensure email is verified
    if not profile.user.verified:
        return False

    # Check if the user has agreed to terms
    if not profile.user.agreed_to_terms:
        return False

    return True
