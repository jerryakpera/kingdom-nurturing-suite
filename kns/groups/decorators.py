"""
Decorators for the `groups` app.
"""

from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Group


def group_leader_required(view_func):
    """
    Decorator that checks if the current user's profile is the leader of the group.

    Parameters
    ----------
    view_func : function
        The view function to be wrapped by this decorator.

    Returns
    -------
    function
        The wrapped view function with group leadership validation.
    """

    @wraps(view_func)
    def _wrapped_view(request, group_slug, *args, **kwargs):
        """
        Wrapped view function that checks for group leadership.

        Parameters
        ----------
        request : HttpRequest
            The incoming request object.
        group_slug : str
            The slug identifying the group from the URL.
        *args : tuple
            Additional positional arguments passed to the view.
        **kwargs : dict
            Additional keyword arguments passed to the view.

        Returns
        -------
        HttpResponse
            The response from the original view if the user is the group leader.

        Raises
        ------
        Http404
            If the group does not exist.
        PermissionDenied
            If the current user is not the leader of the group.
        """
        group = get_object_or_404(Group, slug=group_slug)

        if group.leader != request.user.profile:
            raise PermissionDenied("You are not the leader of this group.")

        return view_func(request, group, *args, **kwargs)

    return _wrapped_view
