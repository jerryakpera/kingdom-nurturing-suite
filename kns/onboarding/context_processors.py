"""
Context processors for the `onboarding` app.
"""

from django.shortcuts import get_object_or_404

from .models import ProfileOnboarding


def onboarding_data(request):
    """
    Context processor to provide onboarding data for authenticated users.

    This function checks if the current request is related to the onboarding
    process and provides the relevant onboarding steps and current step data.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    dict
        A dictionary with onboarding steps list and current step data if
        the user is authenticated and the request path includes 'onboarding'.
        Otherwise, returns an empty dictionary.
    """
    if request.user.is_authenticated:
        if "onboarding" in request.path:
            profile = request.user.profile
            profile_onboarding = get_object_or_404(
                ProfileOnboarding,
                profile=profile,
            )

            # Create ProfileOnboarding if it does not exist
            if not profile_onboarding:  # pragma: no cover
                profile_onboarding = ProfileOnboarding.objects.create(
                    profile=profile,
                )

            return {
                "onboarding_steps_list": profile_onboarding.get_onboarding_steps_list(
                    profile
                ),
                "onboarding_data": profile_onboarding.get_current_step(profile),
            }

    return {}
