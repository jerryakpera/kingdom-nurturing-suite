"""
Context processors for the `profiles` app.
"""

from django.http import Http404
from django.shortcuts import get_object_or_404

from .forms import GroupForm
from .models import Group


def group_context(request):
    """
    Context processor to add the group and group form to the context.

    This context processor attempts to retrieve a group based on the slug obtained
    from the request. If the group exists, it also provides a form for editing
    the group.

    Parameters
    ----------
    request : HttpRequest
        A Http Request.

    Returns
    -------
    group : Group
        Group instance.
    group_form : Form
        Form for editing group.
    """

    group = None
    descendants = None
    group_slug = (
        request.resolver_match.kwargs.get("group_slug")
        if request.resolver_match
        else None
    )
    if group_slug:
        try:
            group = get_object_or_404(Group, slug=group_slug)
            descendants = group.get_descendants(include_self=True)
        except Http404:
            # Handle not found case if needed
            group = None

    return {
        "group": group,
        "descendants": descendants,
        "group_settings_form": (GroupForm(instance=group) if group else None),
    }
