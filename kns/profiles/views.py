"""
Views for the profiles app.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Profile


@login_required
def index(request):
    """
    View to render a page displaying a list of all profiles.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.

    Returns
    -------
    HttpResponse
        The rendered template with a list of profiles.
    """
    profiles = Profile.objects.filter(
        first_name__isnull=False,
        last_name__isnull=False,
    ).exclude(
        first_name="",
        last_name="",
    )

    context = {
        "profiles": profiles,
    }

    return render(
        request=request,
        template_name="profiles/pages/index.html",
        context=context,
    )


@login_required
def profile_detail(request, profile_slug):
    """
    View to render a page displaying details for a specific profile.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.
    profile_slug : str
        The slug of the profile to retrieve.

    Returns
    -------
    HttpResponse
        The rendered template with the details of the specified
        profile.

    Raises
    ------
    Profile.DoesNotExist
        If no Profile with the given slug exists.
    """
    profile = get_object_or_404(
        Profile,
        slug=profile_slug,
    )

    context = {
        "profile": profile,
    }

    return render(
        request=request,
        template_name="profiles/pages/profile-detail.html",
        context=context,
    )
