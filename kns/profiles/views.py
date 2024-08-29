"""
Views for the profiles app.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from formtools.wizard.views import SessionWizardView

from kns.accounts import emails as account_emails
from kns.core.utils import log_this
from kns.custom_user.models import User

from . import constants as profile_constants
from . import forms as profile_forms
from .models import ConsentForm, Profile


class NewMemberView(SessionWizardView):  # pragma: no cover
    """
    View for handling the registration of new members through a multi-step form.

    This view uses a wizard pattern to collect and process information about new members.
    The process includes multiple forms that gather various details about the member,
    and upon completion, creates a new user and profile, assigns them to a group, and
    optionally sends welcome emails.

    Attributes
    ----------
    template_name : str
        The template used to render the registration form.
    form_list : list
        A list of form classes used in the registration wizard.

    Methods
    -------
    get_context_data(**kwargs)
        Provides additional context data for rendering the template,
        including form steps and the current step index.
    done(form_list, **kwargs)
        Handles the final step of the wizard. Creates a user and profile
        based on the collected data, assigns the member to a group, and
        manages email notifications.
    """

    template_name = "profiles/pages/register_member.html"
    form_list = [
        profile_forms.BioDetailsForm,
        profile_forms.ContactDetailsForm,
        profile_forms.ProfileInvolvementForm,
        profile_forms.ProfileRoleForm,
    ]

    def get_context_data(self, **kwargs):
        """
        Add additional context data for rendering the registration template.

        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments to pass to the parent context method.

        Returns
        -------
        dict
            The updated context data including form steps and the current step index.
        """
        context = super().get_context_data(**kwargs)
        # Add any additional context data here

        context["form_steps"] = profile_constants.REGISTER_MEMBER_FORM_STEPS
        context["current_step_index"] = self.steps.current

        return context

    def done(self, form_list, **kwargs):
        """
        Handle the final step of the registration wizard. Creates a
        new user and profile based on the cleaned data from the forms,
        assigns the member to the user's group, and manages email
        notifications.

        Parameters
        ----------
        form_list : list
            A list of form instances containing the cleaned data from
            each step of the wizard.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        HttpResponse
            Redirects to the profile page upon successful registration
            or reloads the registration page if errors occur.
        """
        new_profile_data = {}
        for form in form_list:
            if form.is_valid():
                new_profile_data.update(form.cleaned_data)
            else:
                return render(
                    self.request,
                    self.template_name,
                    {
                        "form_list": form_list,
                        "wizard_form_data": self.get_all_cleaned_data(),
                    },
                )

        try:
            user = User.objects.create(
                email=new_profile_data.get("email"),
            )

            # Create the profile associated with the user
            profile, profile_created = Profile.objects.get_or_create(
                user=user, defaults=new_profile_data
            )

            if not profile_created:
                # Update profile data if the profile already exists
                for attr, value in new_profile_data.items():
                    setattr(profile, attr, value)
                profile.save()

            # Add the new member to the users group
            self.request.user.profile.group_led.add_member(profile)

            account_emails.send_welcome_email(
                request=self.request,
                profile=profile,
                leader=self.request.user.profile,
            )

            if profile.role == "leader":
                account_emails.send_set_password_email(
                    request=self.request,
                    profile=profile,
                )

            messages.success(
                request=self.request,
                message=(
                    f"Congratulations, {profile.get_full_name()} is now "
                    "a member of your group. We have sent them an email "
                    "with instructions on how to get started."
                ),
            )

            return redirect(profile)

        except Exception as e:
            log_this(e)
            messages.error(
                request=self.request,
                message=(
                    "An error occurred while trying to create and "
                    "register the member. Please try again."
                ),
            )

            return redirect("profiles:register_member")


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

    profile_settings_form = profile_forms.ProfileSettingsForm(
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

    form = profile_forms.ConsentFormSubmission(
        request.POST or None,
        request.FILES or None,
        instance=consent_form,
    )

    if request.method == "POST":
        form = profile_forms.ConsentFormSubmission(
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
def make_leader_page(request, profile_slug):  # pragma: no cover
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

    return render(
        request=request,
        template_name="profiles/pages/make_leader.html",
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
        account_emails.send_set_password_email(
            request=request,
            profile=profile,
        )

        messages.success(
            request=request,
            message=f"{profile.get_full_name()} has been successfully promoted to a leader.",
        )

    return redirect(profile.get_absolute_url())


@login_required
def edit_bio_details(request, profile_slug):
    """
    Edit the bio details of a user profile.

    This view allows updating the bio details of a profile. It processes
    both GET and POST requests. If the request is POST and the form is valid,
    the profile is updated, and a success message is displayed.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object used to process the request.
    profile_slug : str
        The slug of the profile to edit.

    Returns
    -------
    HttpResponse
        Renders the edit bio details template or redirects to the profile
        detail page with a success message if the form is valid.
    """
    profile = get_object_or_404(
        Profile,
        slug=profile_slug,
    )

    bio_details_form = profile_forms.BioDetailsForm(
        request.POST or None,
        instance=profile,
    )

    context = {
        "can_edit_profile": False,
        "bio_details_form": bio_details_form,
    }

    if request.method == "POST":
        if bio_details_form.is_valid():
            bio_details_form.save()

            messages.success(
                request=request,
                message="Profile updated",
            )

            return redirect(profile)

    return render(
        request=request,
        template_name="profiles/pages/edit_bio_details.html",
        context=context,
    )


@login_required
def edit_contact_details(request, profile_slug):
    """
    Edit the contact details of a user profile.

    This view allows updating the contact details of a profile. It processes
    both GET and POST requests. If the request is POST and the form is valid,
    the profile is updated, and a success message is displayed.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object used to process the request.
    profile_slug : str
        The slug of the profile to edit.

    Returns
    -------
    HttpResponse
        Renders the edit contact details template or redirects to the profile
        detail page with a success message if the form is valid.
    """
    profile = get_object_or_404(
        Profile,
        slug=profile_slug,
    )

    contact_details_form = profile_forms.ContactDetailsForm(
        request.POST or None,
        instance=profile,
        show_email=False,
    )

    context = {
        "can_edit_profile": False,
        "contact_details_form": contact_details_form,
    }

    if request.method == "POST":
        if contact_details_form.is_valid():
            contact_details_form.save()

            messages.success(
                request=request,
                message="Profile contact details updated.",
            )

            return redirect(profile)

    return render(
        request=request,
        template_name="profiles/pages/edit_contact_details.html",
        context=context,
    )


@login_required
def edit_involvement_details(request, profile_slug):
    """
    Edit the involvement details of a user profile.

    This view allows updating the involvement details of a profile. It processes
    both GET and POST requests. If the request is POST and the form is valid,
    the profile is updated, and a success message is displayed.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object used to process the request.
    profile_slug : str
        The slug of the profile to edit.

    Returns
    -------
    HttpResponse
        Renders the edit involvement details template or redirects to the profile
        detail page with a success message if the form is valid.
    """
    profile = get_object_or_404(Profile, slug=profile_slug)

    involvement_form = profile_forms.ProfileInvolvementForm(
        request.POST or None,
        instance=profile,
    )

    context = {
        "can_edit_profile": False,
        "involvement_form": involvement_form,
    }

    if request.method == "POST":
        if involvement_form.is_valid():
            involvement_form.save()

            messages.success(
                request=request,
                message="Profile involvement details updated",
            )

            return redirect(profile)

    return render(
        request=request,
        template_name="profiles/pages/edit_involvement_details.html",
        context=context,
    )
