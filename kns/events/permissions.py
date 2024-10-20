"""
Permission functions for the `events` app.
"""

from django.shortcuts import redirect
from django.urls import reverse_lazy


def has_event_creation_permission(user):
    """
    Check if the user has permission to create an event.

    This function determines whether a given user meets the criteria
    for creating an event. The criteria include being authenticated,
    having a verified profile, and being a leader of a group.

    Parameters
    ----------
    user : User
        The user whose permissions are being checked.

    Returns
    -------
    bool
        True if the user has permission to create an event; otherwise, False.
    """

    # Check if the user is authenticated
    if not user.is_authenticated:
        return False

    # Check if the user's profile is verified
    if not user.verified:
        return False

    # Check if the user's profile is a leader and leading a group
    if not user.profile.is_leading_group():
        return False

    # Add more conditions as needed

    return True


def event_creation_permission_required(view_func):  # pragma: no cover
    """
    Decorator for views that checks whether a user has permission to create an event.

    This decorator wraps a view function and checks if the user has the
    necessary permissions to create an event. If the user lacks the
    required permissions, they are redirected to the index page or
    another specified location.

    Parameters
    ----------
    view_func : callable
        The view function to be wrapped.

    Returns
    -------
    callable
        The wrapped view function that includes permission checking.
    """

    def _wrapped_view(request, *args, **kwargs):
        """
        Inner function that checks the user's event creation permissions.

        This function performs the actual permission check for the user
        attempting to access the view. If the user lacks the required
        permissions, they are redirected to the index page.

        Parameters
        ----------
        request : HttpRequest
            The HTTP request object containing the user details.
        *args : tuple
            Additional positional arguments passed to the view.
        **kwargs : dict
            Additional keyword arguments passed to the view.

        Returns
        -------
        HttpResponse
            The original view's response if permission is granted, or a
            redirect to the index page if permission is denied.
        """
        if not has_event_creation_permission(request.user):
            # Redirect to the index page or any other appropriate page
            return redirect(reverse_lazy("events:index"))

        return view_func(request, *args, **kwargs)

    return _wrapped_view
