"""
Utils for the `onboarding` app.
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from kns.profiles.models import Profile

from .models import ProfileOnboarding


def finish_onboarding(request):  # pragma: no cover
    """
    Mark the user's profile as onboarded and redirect to the profile page.

    This function marks the user's profile as having completed the onboarding process
    by setting the `is_onboarded` field to `True` and saves the profile.
    A success message is also displayed to the user.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object containing the current user's session and data.

    Returns
    -------
    HttpResponseRedirect
        A redirect response to the user's profile page after onboarding completion.
    """
    profile = get_object_or_404(
        Profile,
        email=request.user.email,
    )

    profile.is_onboarded = True
    profile.save()

    messages.success(
        request,
        "Congratulations! You have successfully completed your onboarding.",
    )

    return redirect(profile)


def handle_next_step(request):  # pragma: no cover
    """
    Handle the transition to the next step in the onboarding process.

    This function checks whether the user has reached the last step of the onboarding
    process. If so, it calls `finish_onboarding`. Otherwise, it retrieves the next
    step and redirects the user to the corresponding step.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object containing the current user's session and data.

    Returns
    -------
    HttpResponseRedirect
        A redirect response to either the user's profile page upon completion or
        the next step in the onboarding process.
    """
    profile = get_object_or_404(Profile, email=request.user.email)
    profile_onboarding = get_object_or_404(
        ProfileOnboarding,
        profile=profile,
    )

    if profile_onboarding.is_last_step(profile):
        return finish_onboarding(request)

    next_step = profile_onboarding.get_current_step(profile)

    return redirect(next_step["url_name"])
