"""
Middlewares for the `onboarding` app.
"""

from django.shortcuts import redirect
from django.urls import resolve, reverse


class OnboardingMiddleware:
    """
    Middleware to check if a user has completed the onboarding process.
    Redirects to the 'onboarding:index' if they haven't completed it yet.
    It ignores admin, admin honeypot, api, logout, and onboarding routes.

    Parameters
    ----------
    get_response : callable
        The next middleware or view in the request/response cycle.
    """

    def __init__(self, get_response):
        """
        Initialize the middleware.

        Parameters
        ----------
        get_response : callable
            The next middleware or view in the request/response cycle.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process the request and handle redirection if necessary.

        Checks if the user is authenticated and whether they have completed
        onboarding. If not, it redirects them to the 'onboarding:index' page.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object.

        Returns
        -------
        HttpResponse
            The HTTP response object from the next middleware or a redirect
            to the onboarding step.
        """
        # Only check for authenticated users
        if request.user.is_authenticated:
            # Bypass admin, honeypot, API, logout, and onboarding URLs
            resolved_url = resolve(request.path_info)
            excluded_url_names = [
                "admin:index",
                "logout",
            ]

            # Check for URL patterns that start with certain prefixes
            excluded_paths = [
                "admin/",
                "control-panel/",
                "api/",
                "onboarding/",
            ]

            if resolved_url.url_name in excluded_url_names or any(
                request.path.startswith(p) for p in excluded_paths
            ):
                return self.get_response(request)

            # Check if the user has completed onboarding
            if not request.user.profile.is_onboarded:
                profile_onboarding = getattr(
                    request.user.profile,
                    "onboarding",
                    None,
                )

                if profile_onboarding:
                    current_step = profile_onboarding.get_current_step(
                        request.user.profile
                    )
                    onboarding_url = reverse(current_step["url_name"])

                    # If the user is not on their current onboarding step, redirect them
                    if request.path != onboarding_url:
                        return redirect(onboarding_url)

        # Proceed with the request if onboarding is complete or irrelevant
        return self.get_response(request)
