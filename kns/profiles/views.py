"""
Views for the profiles app.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from kns.accounts.emails import send_set_password_email
from kns.core.models import Setting

from .forms import ConsentFormSubmission, ProfileSettingsForm
from .models import ConsentForm, Profile


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

    context = {}

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
        "profile": profile,
        "profile_settings_form": profile_settings_form,
    }

    return render(
        request=request,
        template_name="profiles/pages/profile_settings.html",
        context=context,
    )


@login_required
def upload_consent_form(request, profile_slug):  # pragma: no cover
    """
    View to render a page allowing the user to upload a consent form.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.
    profile_slug : str
        The slug of the profile to retrieve.

    Returns
    -------
    HttpResponse
        The rendered template with the consent form upload form.
    """
    profile = get_object_or_404(
        Profile,
        slug=profile_slug,
    )

    consent_form = None

    # Ensure a consent form exists for the profile or create a new one
    try:
        consent_form = ConsentForm.objects.get(
            profile=profile,
        )

        if consent_form and consent_form.status != "rejected":
            messages.warning(
                request=request,
                message=(
                    "You cannot submit a consent form for this "
                    "profile at the moment."
                ),
            )
            return redirect(
                "profiles:profile_detail",
                profile_slug=profile.slug,
            )
    except ConsentForm.DoesNotExist:
        consent_form = None

    form = ConsentFormSubmission(
        request.POST or None,
        request.FILES or None,
        instance=consent_form,
    )

    if request.method == "POST":
        form = ConsentFormSubmission(
            request.POST,
            request.FILES,
        )

        try:
            if form.is_valid():
                if consent_form:
                    # Delete the current consent form
                    consent_form.delete()

                # Create new consent form
                consent_form = form.save(commit=False)
                consent_form.profile = profile
                consent_form.submitted_by = request.user.profile

                consent_form.save()

                messages.success(
                    request=request,
                    message="Consent form successfully uploaded.",
                )

                return redirect(
                    "profiles:profile_detail",
                    profile_slug=profile.slug,
                )
            else:
                messages.error(
                    request=request,
                    message="There was an error uploading the consent form.",
                )

        except ValidationError:
            messages.error(
                request=request,
                message="The consent form must be a PDF, JPG, or PNG file.",
            )

    context = {
        "form": form,
        "profile": profile,
    }

    return render(
        request=request,
        template_name="profiles/pages/submit_consent_form.html",
        context=context,
    )


@login_required
def make_leader(request, profile_slug):  # pragma: no cover
    """
    View to promote a user profile to a leader role.

    This view checks if the requesting user has the necessary permissions
    to promote another user to a leader role within a group. If the checks
    pass, the target profile's role is updated to 'leader', and an email is
    sent to the user to set their password.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object used to process the request.
    profile_slug : str
        The slug of the profile to retrieve and promote.

    Returns
    -------
    HttpResponse
        Redirects to the profile detail page with a success or error message.
    """

    # Fetch the profile or return a 404 if not found
    profile = get_object_or_404(Profile, slug=profile_slug)

    # Ensure the requesting user is leading the profile's group
    if not request.user.profile.group_led.is_member(profile):
        messages.error(
            request=request,
            message=f"You must be the leader of {profile.get_full_name()} to perform this action.",
        )

        return redirect(profile.get_absolute_url())

    # Verify that the profile can be made into a leader
    if not profile.can_become_leader_role():
        messages.error(
            request=request,
            message=f"{profile.get_full_name()} is not eligible to become a leader.",
        )

        return redirect(profile.get_absolute_url())

    profile.change_role_to_leader(request.user.profile)

    if request.user.profile.needs_approval_to_change_group_members_role():
        # User needs approval
        messages.success(
            request=request,
            message=(
                f"You have submitted a request to change "
                f"{profile.get_full_name()} to a leader role"
            ),
        )
    else:
        # Send the set password email
        send_set_password_email(
            request=request,
            profile=profile,
            leader=request.user.profile,
        )

        messages.success(
            request=request,
            message=f"{profile.get_full_name()} has been successfully promoted to a leader.",
        )

    return redirect(profile.get_absolute_url())
