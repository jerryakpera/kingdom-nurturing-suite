"""
Views for the profiles app.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileSettingsForm
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
        template_name="profiles/pages/profile_detail.html",
        context=context,
    )


@login_required
def profile_involvements(request, profile_slug):
    """
    View to render a page displaying involvements for a specific profile.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.
    profile_slug : str
        The slug of the profile to retrieve.

    Returns
    -------
    HttpResponse
        The rendered template with the involvements of the specified
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
        template_name="profiles/pages/profile_involvements.html",
        context=context,
    )


@login_required
def profile_trainings(request, profile_slug):
    """
    View to render a page displaying trainings for a specific profile.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.
    profile_slug : str
        The slug of the profile to retrieve.

    Returns
    -------
    HttpResponse
        The rendered template with the trainings of the specified
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
        template_name="profiles/pages/profile_trainings.html",
        context=context,
    )


@login_required
def profile_activities(request, profile_slug):
    """
    View to render a page displaying activities for a specific profile.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.
    profile_slug : str
        The slug of the profile to retrieve.

    Returns
    -------
    HttpResponse
        The rendered template with the activities of the specified
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
        template_name="profiles/pages/profile_activities.html",
        context=context,
    )


@login_required
def profile_settings(request, profile_slug):
    """
    View to render a page displaying settings for a specific profile.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.
    profile_slug : str
        The slug of the profile to retrieve.

    Returns
    -------
    HttpResponse
        The rendered template with the settings of the specified
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

    profile_settings_form = ProfileSettingsForm(
        request.POST or None,
        instance=profile,
    )

    if request.method == "POST":
        if profile_settings_form.is_valid():
            profile_settings_form.save()

            messages.success(
                request,
                f"{profile.get_full_name()} settings updated",
            )

            return redirect(profile)

    context = {
        "profile_settings_form": profile_settings_form,
    }

    return render(
        request=request,
        template_name="profiles/pages/profile_settings.html",
        context=context,
    )
