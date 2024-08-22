"""
Context processors for the `profiles` app.
"""

from django.http import Http404
from django.shortcuts import get_object_or_404

from .forms import ProfileSettingsForm
from .models import Profile


def user_profile_context(request):
    """
    Context processor to add the current user's profile to the context.

    Parameters
    ----------
    request : HttpRequest
        The request object.

    Returns
    -------
    dict
        A dictionary containing the current user's profile.
    """

    context = {}

    if request.user.is_authenticated:
        try:
            context["my_profile"] = request.user.profile
        except Profile.DoesNotExist:
            pass

    return context


def profile_context(request):
    """
    Context processor to add the profile and profile settings form to the context.

    This context processor attempts to retrieve a profile based on the slug obtained
    from the request. If the profile exists, it also provides a form for editing
    profile settings.

    Parameters
    ----------
    request : HttpRequest
        A Http Request.

    Returns
    -------
    profile : Profile
        Profile instance.
    profile_settings : Form
        Form for editing profile settings.
    """

    profile = None
    profile_slug = (
        request.resolver_match.kwargs.get("profile_slug")
        if request.resolver_match
        else None
    )
    if profile_slug:
        try:
            profile = get_object_or_404(
                Profile,
                slug=profile_slug,
            )
        except Http404:
            # Handle not found case if needed
            profile = None

    return {
        "profile": profile,
        "profile_settings_form": (
            ProfileSettingsForm(instance=profile) if profile else None
        ),
    }
