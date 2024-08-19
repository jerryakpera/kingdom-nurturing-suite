"""
Views for the `groups` app.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from kns.groups.models import Group


@login_required
def index(request):
    """
    View function to display a list of all groups.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse:
        The rendered template displaying the list of groups.
    """
    groups = Group.objects.all()

    context = {
        "groups": groups,
    }

    return render(
        request=request,
        template_name="groups/pages/index.html",
        context=context,
    )


@login_required
def group_detail(request, group_slug):
    """
    View function to display the details of a specific group.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    group_slug : str
        The slug of the group to display.

    Returns
    -------
    HttpResponse:
        The rendered template displaying the details of the group.
    """
    group = get_object_or_404(
        Group,
        slug=group_slug,
    )

    context = {
        "group": group,
    }

    return render(
        request=request,
        template_name="groups/pages/group_detail.html",
        context=context,
    )
