"""
Context processors for the `profiles` app.
"""

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from kns.groups.models import GroupMember

from .forms import ProfileSettingsForm
from .models import Profile
from .utils import get_profile_slug


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
    profile settings. It includes a check to determine if the user is a member
    of the group led by the profile's group, though this information is not used
    in the context.

    Parameters
    ----------
    request : HttpRequest
        The request object.

    Returns
    -------
    dict
        A dictionary containing the profile and the profile settings form if the
        profile exists, otherwise an empty dictionary.
    """
    context = {}
    slug = get_profile_slug(request)

    if slug:
        # Attempt to retrieve the profile; this will raise Http404
        # if the profile does not exist
        profile = get_object_or_404(Profile, slug=slug)

        profile_settings_form = ProfileSettingsForm(instance=profile)

        try:
            # Check if the user is a member of the group led by the
            # profile's group
            GroupMember.objects.filter(
                group=request.user.profile.group_led,
                profile=profile,
            ).exists()
        except ObjectDoesNotExist:
            pass

        context = {
            "profile": profile,
            "profile_settings_form": profile_settings_form,
        }

    return context
