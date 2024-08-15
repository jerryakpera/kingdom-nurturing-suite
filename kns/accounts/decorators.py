"""
Decorators for the accounts app.
"""

from django.shortcuts import redirect
from django.urls import reverse


def guest_required(view_func):
    """
    Decorator to redirect authenticated users away from a view.

    If the user is already authenticated, this decorator redirects them to
    a specified page, typically the home or dashboard page. If the user is
    not authenticated, the original view function is called.

    Parameters
    ----------
    view_func : function
        The view function to be decorated.

    Returns
    -------
    function
        A wrapped view function that handles the redirection for authenticated users.
    """

    def _wrapped_view(request, *args, **kwargs):
        """
        Wrapper function that performs the redirection if the user is authenticated.

        Checks if the user is authenticated. If so, it redirects the user to
        the specified page (e.g., the home or dashboard page). If the user
        is not authenticated, it calls the original view function with the
        provided arguments.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object.

        *args : tuple
            Positional arguments passed to the original view function.

        **kwargs : dict
            Keyword arguments passed to the original view function.

        Returns
        -------
        HttpResponse
            A redirect response if the user is authenticated, or the result
            of the original view function if not.
        """

        if request.user.is_authenticated:
            # Redirect to the default page
            return redirect(reverse("accounts:index"))

        return view_func(request, *args, **kwargs)

    return _wrapped_view
