"""
Decorators for the `profiles` app.
"""

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import Profile


def profile_required(redirect_url="/profile/"):
    """
    Decorator to ensure the user has a profile attached.

    Parameters
    ----------
    redirect_url : str
        The URL to redirect to if the user has no profile.

    Returns
    -------
    function
        The decorated view function.
    """

    def decorator(view_func):
        """
        Wrap the given view function to check if the user has a profile.

        Parameters
        ----------
        view_func : function
            The view function to be decorated.

        Returns
        -------
        function
            The wrapped view function.
        """

        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            """
            Check if the user is authenticated and has a profile.

            Parameters
            ----------
            request : HttpRequest
                The request object used to generate the response.
            *args : tuple
                Variable length argument list for the view function.
            **kwargs : dict
                Arbitrary keyword arguments for the view function.

            Returns
            -------
            HttpResponse
                The response from the original view or a redirect.
            """
            # Check if the user is authenticated and has a profile
            if request.user.is_authenticated:
                try:
                    if request.user.profile:
                        return view_func(request, *args, **kwargs)
                except Profile.DoesNotExist:
                    pass

            # If the profile does not exist,
            # redirect to the specified URL
            messages.error(
                request=request,
                message="You need a profile to access that page.",
            )
            return redirect(redirect_url)

        return _wrapped_view

    return decorator
