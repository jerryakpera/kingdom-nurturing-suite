"""
Views for the `Onboarding` app.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from kns.core.utils import log_this
from kns.groups.forms import GroupForm
from kns.groups.models import Group, GroupMember
from kns.profiles.forms import AgreeToTermsForm, BioDetailsForm, ProfileInvolvementForm
from kns.profiles.models import Profile

from .models import ProfileOnboarding
from .utils import handle_next_step


@login_required
def back(request):
    """
    Go back to the previous step in the onboarding process.

    This view moves the user's onboarding process to the previous step
    by calling the `back` method on the `ProfileOnboarding` model.
    After moving to the previous step, it redirects the user to the URL
    associated with the new current step.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        A redirect response to the current step's URL.
    """
    # Retrieve the user's profile onboarding instance
    profile_onboarding = get_object_or_404(
        ProfileOnboarding, profile=request.user.profile
    )

    # Move back to the previous step
    profile_onboarding.back()

    # Retrieve the updated current step
    current_step = profile_onboarding.get_current_step(profile_onboarding.profile)

    # Redirect to the URL of the current step
    return redirect(current_step["url_name"])


@login_required
def index(request):
    """
    Render the onboarding index page.

    This view serves as the landing page for the onboarding process.
    It retrieves the current onboarding step and displays the profile
    details form for the user to confirm or update their details.

    If the form is valid upon submission, it saves the updated profile
    details and progresses the onboarding process to the next step.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        A response rendering the onboarding index page with the profile
        details form.
    """
    profile = get_object_or_404(Profile, email=request.user.email)
    profile_onboarding = get_object_or_404(
        ProfileOnboarding,
        profile=profile,
    )

    onboarding_data = profile_onboarding.get_current_step(
        request.user.profile,
    )

    bio_details_form = BioDetailsForm(
        request.POST or None,
        instance=profile,
    )

    if request.method == "POST":
        if bio_details_form.is_valid():
            bio_details_form.save()

            profile_onboarding.next(profile=profile)
            return handle_next_step(request)

    profile.create_profile_completion_tasks()

    context = {
        "onboarding_data": onboarding_data,
        "bio_details_form": bio_details_form,
    }

    return render(
        request=request,
        template_name="onboarding/pages/bio_details.html",
        context=context,
    )


@login_required
def involvement(request):
    """
    Render the involvement onboarding page.

    This view handles the onboarding step where users confirm their
    involvement details. It displays a form for users to update their
    involvement in the organization.

    If the form is valid upon submission, it saves the involvement
    details and progresses the onboarding process to the next step.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        A response rendering the involvement onboarding page with the
        involvement form.
    """
    profile = get_object_or_404(
        Profile,
        email=request.user.email,
    )
    profile_onboarding = get_object_or_404(
        ProfileOnboarding,
        profile=profile,
    )

    onboarding_data = profile_onboarding.get_current_step(
        request.user.profile,
    )

    involvement_form = ProfileInvolvementForm(
        request.POST or None,
        instance=profile,
    )

    if request.method == "POST":
        if involvement_form.is_valid():
            involvement_form.save()

            profile_onboarding.next(profile=profile)
            return handle_next_step(request)

    context = {
        "onboarding_data": onboarding_data,
        "involvement_form": involvement_form,
    }

    return render(
        request=request,
        template_name="onboarding/pages/involvement_details.html",
        context=context,
    )


@login_required
def group(request):
    """
    Render the group onboarding page.

    This view handles the onboarding step where users create or update
    a group they are leading. It displays a form for users to either
    register a new group or update an existing one if they are already
    leading a group.

    If the form is valid upon submission, it saves the group details
    and progresses the onboarding process to the next step.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        A response rendering the group onboarding page with the group form.
    """
    profile = get_object_or_404(Profile, email=request.user.email)
    profile_onboarding = get_object_or_404(ProfileOnboarding, profile=profile)

    onboarding_data = profile_onboarding.get_current_step(request.user.profile)

    group_led = Group.objects.filter(leader=profile).exists()

    if group_led:
        group = Group.objects.get(leader=profile)
        group_form = GroupForm(request.POST or None, instance=group)
    else:
        group_form = GroupForm(request.POST or None)

    if request.method == "POST":
        group_led = Group.objects.filter(leader=profile).exists()

        if not group_led:
            if group_form.is_valid():
                group = group_form.save(commit=False)

                # Process uploaded images, if any
                for image in request.FILES.getlist("image"):  # pragma: no cover
                    group.image = image

                # Set parent group if user belongs to a group
                try:
                    group_member = GroupMember.objects.get(profile=profile)
                    group.parent = group_member.group  # pragma: no cover
                except GroupMember.DoesNotExist:
                    pass

                group.leader = profile
                group.save()

                # Move to the next step in onboarding
                profile_onboarding.next(profile=profile)
                return handle_next_step(request)

    # If the form is invalid or if the request is not POST, stay on the same page
    context = {
        "group_form": group_form,
        "onboarding_data": onboarding_data,
    }

    return render(
        request=request,
        template_name="onboarding/pages/register_group_onboarding.html",
        context=context,
    )


@login_required
def agree(request):
    """
    Render the agree to terms onboarding page.

    This view handles the onboarding step where users confirm their
    agreement to the terms. It displays a form for users to agree to
    the terms of the organization.

    If the form is valid upon submission, it updates the profile to
    reflect the agreement and progresses the onboarding process to
    the next step.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        A response rendering the agree to terms onboarding page with
        the agreement form.
    """
    profile = get_object_or_404(Profile, email=request.user.email)
    profile_onboarding = get_object_or_404(
        ProfileOnboarding,
        profile=profile,
    )

    onboarding_data = profile_onboarding.get_current_step(
        request.user.profile,
    )

    agree_form = AgreeToTermsForm(
        request.POST or None,
        instance=profile,
    )

    if request.method == "POST":
        if agree_form.is_valid():
            agree_form.save()

            profile.user.verified = True
            profile.user.agreed_to_terms = True
            profile.user.save()

            profile_onboarding.current_step = profile_onboarding.current_step + 1

            profile_onboarding.save()

            return handle_next_step(request)

    context = {
        "agree_form": agree_form,
        "onboarding_data": onboarding_data,
    }

    return render(
        request=request,
        template_name="onboarding/pages/agree_to_terms_onboarding.html",
        context=context,
    )
