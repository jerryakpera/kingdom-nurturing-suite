"""
This module contains utility methods for managing and interacting with
Profile objects.
"""

from datetime import date

from django.urls import reverse


def can_become_external_person_role(profile):
    """
    Determine if the profile can become an external person.

    Parameters
    ----------
    profile : Profile
        The profile instance.

    Returns
    -------
    bool
        True if the profile can become an external person, False otherwise.
    """

    if not profile.is_profile_complete():
        return False

    if profile.role == "external_person":
        return False

    if profile.is_leading_group():
        return False

    return True


def can_become_leader_role(profile):
    """
    Determine if the profile can become a leader.

    Parameters
    ----------
    profile : Profile
        The profile instance.

    Returns
    -------
    bool
        True if the profile can become a leader, False otherwise.
    """
    if not profile.is_profile_complete():
        return False

    if profile.role == "leader":
        return False

    if profile.needs_consent_form():
        return False

    return True


def can_become_member_role(profile):
    """
    Determine if the profile can become a member.

    Parameters
    ----------
    profile : Profile
        The profile instance.

    Returns
    -------
    bool
        True if the profile can become a member, False otherwise.
    """
    if profile.role == "member":
        return False

    if profile.is_leading_group():
        return False

    return True


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
        "profiles:profile_overview",
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


def get_age(profile):
    """
    Calculate and return the profile's age based on date_of_birth.

    Parameters
    ----------
    profile : Profile
        The profile instance.

    Returns
    -------
    int
        The age of the profile instance, or None if date_of_birth is not set.
    """
    if profile.date_of_birth:
        today = date.today()
        return (
            today.year
            - profile.date_of_birth.year
            - (
                (today.month, today.day)
                < (profile.date_of_birth.month, profile.date_of_birth.day)
            )
        )

    return None


def get_current_consent_form(profile):
    """
    Get the current consent form associated with the profile.

    Parameters
    ----------
    profile : Profile
        The profile instance.

    Returns
    -------
    ConsentForm or None
        The current consent form for the profile instance, or None if not present.
    """
    return profile.consent_form if hasattr(profile, "consent_form") else None


def get_discipleships_url(profile):
    """
    Return the discipleships URL to access a detail view of this profile.

    Parameters
    ----------
    profile : Profile
        The profile instance.

    Returns
    -------
    str
        The discipleships URL of the profile's detail view.
    """
    return reverse(
        "profiles:profile_discipleships",
        kwargs={
            "profile_slug": profile.slug,
        },
    )


def get_mentorships_url(profile):
    """
    Return the mentorships URL to access a detail view of this profile.

    Parameters
    ----------
    profile : Profile
        The profile instance.

    Returns
    -------
    str
        The mentorships URL of the profile's detail view.
    """
    return reverse(
        "profiles:profile_mentorships",
        kwargs={
            "profile_slug": profile.slug,
        },
    )


def get_role_display_str(profile):
    """
    Return the string display for this profile's role.

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
        True if the user meets all eligibility criteria, False otherwise.
    """
    # Check if the user is a visitor
    if profile.user.is_visitor:
        return False

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

    # Check if the profile is fully completed
    if not profile.is_profile_complete():
        return False

    return True


def is_leading_group(profile):
    """
    Return whether the profile instance is leading a group.

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
        True if all required fields are filled out and additional criteria are met,
        False otherwise.
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


def is_under_age(profile, adult_age):
    """
    Determine if the profile is under age based on the date_of_birth
    and the adult_age setting.

    Parameters
    ----------
    profile : Profile
        The profile instance.
    adult_age : int
        Age that is set as the adult age.

    Returns
    -------
    bool
        True if the profile's age is below the specified adult age, False otherwise.
    """
    if profile.date_of_birth:
        today = date.today()
        age = (
            today.year
            - profile.date_of_birth.year
            - (
                (today.month, today.day)
                < (profile.date_of_birth.month, profile.date_of_birth.day)
            )
        )
        return age < adult_age

    return True
