"""
Middlewares for the `onboarding` app.
"""

import logging

from django.shortcuts import get_object_or_404, redirect
from django.urls import resolve, reverse

from kns.onboarding.models import ProfileOnboarding
from kns.profiles.models import Profile

logger = logging.getLogger(__name__)


class OnboardingMiddleware:  # pragma: no cover
    """
    Middleware to handle the onboarding process for authenticated users.

    This middleware ensures that users who have not completed the onboarding
    process are redirected to the appropriate onboarding step if they attempt
    to access any route that is not related to onboarding, admin, or logout.

    Parameters
    ----------
    get_response : callable
        The next middleware or view in the request/response cycle.
    """

    def __init__(self, get_response):
        """
        Initialize the OnboardingMiddleware.

        Parameters
        ----------
        get_response : callable
            The next middleware or view in the request/response cycle.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process the request and handle redirection if necessary.

        Checks if the user is authenticated and has not completed the onboarding
        process. If so, redirects them to the current onboarding step unless
        they are accessing an admin, logout, or onboarding route.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object.

        Returns
        -------
        HttpResponse
            The HTTP response object from the next middleware or view, or a
            redirection response if the user needs to complete onboarding.
        """
        if request.user.is_authenticated:
            if not request.user.profile.is_onboarded:
                resolved_url = resolve(request.path_info)
                if resolved_url.url_name in [
                    "admin:index",
                    "logout",
                ] or resolved_url.url_name.startswith("onboarding"):
                    return self.get_response(request)

                profile = get_object_or_404(
                    Profile,
                    email=request.user.email,
                )
                profile_onboarding, created = ProfileOnboarding.objects.get_or_create(
                    profile=profile
                )

                current_step = profile_onboarding.get_current_step(request.user.profile)

                logger.debug(
                    "Redirecting to onboarding step: %s", current_step["url_name"]
                )
                return redirect(reverse(current_step["url_name"]))

        response = self.get_response(request)
        return response
