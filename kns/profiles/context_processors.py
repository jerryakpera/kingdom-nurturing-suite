"""
Context processors for the `profiles` app.
"""

from django.http import Http404
from django.shortcuts import get_object_or_404

from kns.groups.models import GroupMember

from .forms import ProfileSettingsForm
from .models import Profile


def profile_context(request):
    """
    Context processor for a single profile.

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
    is_member_of_user_group = False
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

            # Check if the profile is a member of any of the request user's groups
            if request.user.is_authenticated:
                is_member_of_user_group = GroupMember.objects.filter(
                    profile=profile, group__leader=request.user.profile
                ).exists()

        except Http404:
            # Handle not found case if needed
            profile = None

    return {
        "profile": profile,
        "is_member_of_user_group": is_member_of_user_group,
        "profile_settings_form": (
            ProfileSettingsForm(instance=profile) if profile else None
        ),
    }
