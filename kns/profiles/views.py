"""
Views for the profiles app.
"""

from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from faker import Faker
from formtools.wizard.views import SessionWizardView

from kns.accounts import emails as account_emails
from kns.classifications.forms import ProfileClassificationForm
from kns.classifications.models import (
    Classification,
    ProfileClassification,
    Subclassification,
)
from kns.core import emails as core_emails
from kns.core import utils as core_utils
from kns.custom_user.models import User
from kns.faith_milestones.forms import ProfileFaithMilestonesForm
from kns.faith_milestones.models import ProfileFaithMilestone
from kns.groups.forms import MoveToChildGroupForm, MoveToSisterGroupForm
from kns.groups.models import Group
from kns.levels.forms import ProfileLevelForm
from kns.levels.models import Level, ProfileLevel, Sublevel
from kns.mentorships.forms import ProfileMentorshipAreasForm
from kns.mentorships.models import ProfileMentorshipArea
from kns.skills.forms import ProfileSkillsForm
from kns.skills.models import ProfileInterest, ProfileSkill
from kns.vocations.forms import ProfileVocationForm
from kns.vocations.models import ProfileVocation

from . import constants as profile_constants
from . import forms as profile_forms
from .models import ConsentForm, EncryptionReason, Profile, ProfileEncryption
from .utils import name_with_apostrophe


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
                user=user,
                defaults=new_profile_data,
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
            core_utils.log_this(e)
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
    View to render a list of profiles with various filtering options.

    This view retrieves profiles from the database and applies filters
    based on user-provided criteria. It displays profiles related to
    the user's group and its descendant groups if applicable. The
    view also paginates the profiles for easier navigation.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object that contains metadata about the request.

    Returns
    -------
    HttpResponse
        An HTTP response object with the rendered template containing the
        filtered profiles and any relevant filter forms.
    """
    profiles = (
        Profile.objects.filter(
            first_name__isnull=False,
            last_name__isnull=False,
        )
        .exclude(
            first_name="",
            last_name="",
        )
        .order_by("created_at")
    )

    # Define a map for sortable fields
    sortable_fields = {
        "last_name": "last_name",
        "first_name": "first_name",
        "created_at": "created_at",
    }

    # Get the sorting parameter from the request
    sort_by = request.GET.get("sort_by", "created_at")
    sort_order = request.GET.get("order", "asc")

    # Ensure the requested sort field is valid
    if sort_by in sortable_fields:
        order_prefix = "-" if sort_order == "desc" else ""
        profiles = profiles.order_by(f"{order_prefix}{sortable_fields[sort_by]}")

    # Get the current user's group
    user_profile = request.user.profile
    users_group = (
        user_profile.group_in.group
        if hasattr(
            user_profile,
            "group_in",
        )
        else None
    )

    if users_group:  # pragma: no cover
        # Get all descendant groups of the user's group
        descendant_groups = users_group.get_descendants(
            include_self=True,
        )
        # Filter profiles to include only those in the descendant groups
        profiles = profiles.filter(
            group_in__group__in=descendant_groups,
        )

    # Initialize filter forms
    basic_info_form = profile_forms.BasicInfoFilterForm(request.GET or None)
    mentorship_form = profile_forms.MentorshipFilterForm(request.GET or None)
    faith_milestones_form = profile_forms.FaithMilestoneFilterForm(request.GET or None)
    involvement_filter_form = profile_forms.InvolvementFilterForm(
        request.GET or None,
    )
    skills_filter_form = profile_forms.SkillsFilterForm(
        request.GET or None,
    )

    # Apply filters based on form data
    if request.method == "GET":
        # Search functionality
        search_query = request.GET.get("search")
        if search_query:
            profiles = profiles.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
            )

        if basic_info_form.is_valid():
            role = basic_info_form.cleaned_data.get("role")
            gender = basic_info_form.cleaned_data.get("gender")
            min_age = basic_info_form.cleaned_data.get("min_age")
            place_of_birth_country = basic_info_form.cleaned_data.get(
                "place_of_birth_country",
            )
            place_of_birth_city = basic_info_form.cleaned_data.get(
                "place_of_birth_city",
            )
            location_country = basic_info_form.cleaned_data.get(
                "location_country",
            )
            location_city = basic_info_form.cleaned_data.get("location_city")

            if role:
                profiles = profiles.filter(role=role)
            if gender:
                profiles = profiles.filter(gender=gender)
            if min_age:
                today = date.today()
                min_birth_date = today - timedelta(days=min_age * 365)

                profiles = profiles.filter(date_of_birth__lte=min_birth_date)

            # Apply place_of_birth_country filter
            if place_of_birth_country:
                profiles = profiles.filter(
                    place_of_birth_country=place_of_birth_country,
                )

            # Apply place_of_birth_city filter
            if place_of_birth_city:
                profiles = profiles.filter(
                    place_of_birth_city__icontains=place_of_birth_city,
                )

            # Apply location_country filter
            if location_country:
                profiles = profiles.filter(
                    location_country=location_country,
                )

            # Apply location_city filter
            if location_city:
                profiles = profiles.filter(
                    location_city__icontains=location_city,
                )

        if involvement_filter_form.is_valid():
            # Process activity training filter form data
            is_movement_training_facilitator = involvement_filter_form.cleaned_data.get(
                "is_movement_training_facilitator"
            )
            is_skill_training_facilitator = involvement_filter_form.cleaned_data.get(
                "is_skill_training_facilitator"
            )
            is_mentor = involvement_filter_form.cleaned_data.get(
                "is_mentor",
            )

            if is_movement_training_facilitator:
                profiles = profiles.filter(
                    is_movement_training_facilitator=True,
                )
            if is_skill_training_facilitator:
                profiles = profiles.filter(
                    is_skill_training_facilitator=True,
                )
            if is_mentor:
                profiles = profiles.filter(
                    is_mentor=True,
                )

        if skills_filter_form.is_valid():
            # Process education and experience filter form data
            skills = skills_filter_form.cleaned_data.get("skills")
            interests = skills_filter_form.cleaned_data.get("interests")
            vocations = skills_filter_form.cleaned_data.get("vocations")

            if skills:
                profiles = profiles.filter(
                    skills__skill__in=skills,
                ).distinct()
            if interests:
                profiles = profiles.filter(
                    interests__interest__in=interests,
                ).distinct()
            if vocations:
                profiles = profiles.filter(
                    vocations__vocation__in=vocations,
                ).distinct()

        if mentorship_form.is_valid():
            # Process mentorship filter form data
            mentorship_areas = mentorship_form.cleaned_data.get(
                "mentorship_areas",
            )

            if mentorship_areas:
                profiles = profiles.filter(
                    mentorship_areas__mentorship_area__in=mentorship_areas,
                )

        if faith_milestones_form.is_valid():
            faith_milestones = faith_milestones_form.cleaned_data.get(
                "faith_milestones",
            )

            if faith_milestones:
                profiles = profiles.filter(
                    faith_milestones__faith_milestone__in=faith_milestones,
                )

    # Pagination
    paginator = Paginator(profiles, 12)
    page = request.GET.get("page")

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:  # pragma: no cover
        page_obj = paginator.page(paginator.num_pages)

    context = {
        "sort_by": sort_by,
        "page_obj": page_obj,
        "page_obj": page_obj,
        "sort_order": sort_order,
        "search_query": search_query,
        "basic_info_form": basic_info_form,
        "mentorship_form": mentorship_form,
        "skills_filter_form": skills_filter_form,
        "faith_milestones_form": faith_milestones_form,
        "involvement_filter_form": involvement_filter_form,
    }

    return render(
        request=request,
        template_name="profiles/pages/index.html",
        context=context,
    )


@login_required
def profile_overview(request, profile_slug):
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

    classifications = ", ".join(
        [pc.classification.title for pc in profile.current_classifications()]
    )

    # Get comma-separated string of subclassifications
    subclassifications = ", ".join(
        [
            pc.subclassification.title
            for pc in profile.current_classifications()
            if pc.subclassification
        ]
    )

    profile_classifications = ProfileClassification.objects.filter(
        profile=profile,
    ).order_by(
        "-created_at",
    )

    profile_classification_no = 1

    if len(profile_classifications) > 0:
        profile_classification = profile_classifications.first()
        profile_classification_no = profile_classification.no + 1

    context = {
        "classifications": classifications,
        "subclassifications": subclassifications,
        "profile_classification_no": profile_classification_no,
    }

    return render(
        request=request,
        template_name="profiles/pages/profile_overview.html",
        context=context,
    )


@login_required
def profile_levels(request, profile_slug):
    """
    View to render a page displaying levels history for a specific profile.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.
    profile_slug : str
        The slug of the profile to retrieve.

    Returns
    -------
    HttpResponse
        The rendered template with the levels history of the specified
        profile.

    Raises
    ------
    Profile.DoesNotExist
        If no Profile with the given slug exists.
    """
    profile = get_object_or_404(Profile, slug=profile_slug)

    profile_levels = ProfileLevel.objects.filter(
        profile=profile,
    ).order_by("-created_at")

    context = {
        "profile_levels": profile_levels,
    }

    return render(
        request=request,
        template_name="levels/pages/profile_levels.html",
        context=context,
    )


@login_required
def profile_classifications(request, profile_slug):
    """
    View to render a page displaying classifications history for a specific profile.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.
    profile_slug : str
        The slug of the profile to retrieve.

    Returns
    -------
    HttpResponse
        The rendered template with the classifications history of the specified
        profile.

    Raises
    ------
    Profile.DoesNotExist
        If no Profile with the given slug exists.
    """
    profile = get_object_or_404(Profile, slug=profile_slug)

    profile_classifications = ProfileClassification.objects.filter(
        profile=profile,
    )

    classification_nos = []
    for pc in profile_classifications:
        classification_nos.append(pc.no)

    classification_nos = list(set(classification_nos))
    classification_nos.sort(reverse=True)

    profile_classifications_group = []

    for no in classification_nos:
        profile_classification_group = ProfileClassification.objects.filter(
            profile=profile,
            no=no,
        )
        profile_classifications_group.append(profile_classification_group)

    context = {
        "profile_classifications_group": profile_classifications_group,
    }

    return render(
        request=request,
        template_name="classifications/pages/profile_classifications.html",
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
                "profiles:profile_overview",
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
                    "profiles:profile_overview",
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
def make_leader_page(request, profile_slug):
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
    profile = get_object_or_404(
        Profile,
        slug=profile_slug,
    )

    if not request.user.profile.is_leading_group():
        return redirect(profile.get_absolute_url())

    # Ensure the requesting user is leading the profile's group
    if not request.user.profile.group_led.is_member(profile):
        messages.error(
            request=request,
            message=f"You must be the leader of {profile.get_full_name()} to perform this action.",
        )

        return redirect(profile.get_absolute_url())

    return render(
        request=request,
        template_name="profiles/pages/make_leader.html",
    )


@login_required
def make_leader(request, profile_slug):
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

    profile.change_role_to_leader()
    profile.send_email_to_new_leader(request=request)  # pragma: no cover

    messages.success(
        request=request,
        message=f"{profile.get_full_name()} has been successfully promoted to a leader.",
    )

    return redirect(profile.get_absolute_url())


@login_required
def make_external_person_page(request, profile_slug):
    """
    View to display the HTML for changing the profiles role to an external person role.

    This view checks if the requesting user has the necessary permissions
    to change a group members profile to an external person role. If the checks
    pass, the target profile's role is updated to 'external_person', and an email is
    sent to the users email notifying them of the change.

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
    profile = get_object_or_404(
        Profile,
        slug=profile_slug,
    )

    if not request.user.profile.is_leading_group():
        return redirect(profile.get_absolute_url())

    # Ensure the requesting user is leading the profile's group
    if not request.user.profile.group_led.is_member(profile):
        messages.error(
            request=request,
            message=f"You must be the leader of {profile.get_full_name()} to perform this action.",
        )

        return redirect(profile.get_absolute_url())

    return render(
        request=request,
        template_name="profiles/pages/make_external_person.html",
    )


@login_required
def make_external_person(request, profile_slug):
    """
    View to change a user profile to an external person role.

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

    if not request.user.profile.is_leading_group():
        return redirect(profile.get_absolute_url())

    # Ensure the requesting user is leading the profile's group
    if not request.user.profile.group_led.is_member(profile):
        messages.error(
            request=request,
            message=f"You must be the leader of {profile.get_full_name()} to perform this action.",
        )

        return redirect(profile.get_absolute_url())

    # Verify that the profile can be made into an external person
    if not profile.can_become_external_person_role():
        messages.error(
            request=request,
            message=f"{profile.get_full_name()} is not eligible to become an external person.",
        )

        return redirect(profile.get_absolute_url())

    profile.change_role_to_external_person()
    profile.send_email_to_new_external_person(request=request)  # pragma: no cover

    messages.success(
        request=request,
        message=f"{profile.get_full_name()} is now an external person.",
    )

    return redirect(profile.get_absolute_url())


@login_required
def make_member_page(request, profile_slug):
    """
    View to demote a user profile to a member role.

    This view checks if the requesting user has the necessary permissions
    to demote another user to a member role within a group. If the checks
    pass, the target profile's role is updated to 'member', and an email is
    sent to the user to set their password.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object used to process the request.
    profile_slug : str
        The slug of the profile to retrieve and demote.

    Returns
    -------
    HttpResponse
        Redirects to the profile detail page with a success or error message.
    """

    # Fetch the profile or return a 404 if not found
    profile = get_object_or_404(
        Profile,
        slug=profile_slug,
    )

    # Ensure the requesting user is leading the profile's group
    if not request.user.profile.group_led.is_member(profile):
        messages.error(
            request=request,
            message=f"You must be the leader of {profile.get_full_name()} to perform this action.",
        )

        return redirect(profile.get_absolute_url())

    return render(
        request=request,
        template_name="profiles/pages/make_member.html",
    )


@login_required
def make_member(request, profile_slug):
    """
    View to promote a user profile to a member role.

    This view checks if the requesting user has the necessary permissions
    to promote another user to a member role within a group. If the checks
    pass, the target profile's role is updated to 'member', and an email is
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

    # Verify that the profile can be made into a member
    if not profile.can_become_member_role():
        messages.error(
            request=request,
            message=f"{profile.get_full_name()} is not eligible to become a member.",
        )

        return redirect(profile.get_absolute_url())

    profile.change_role_to_member()
    profile.send_email_to_new_member(request=request)  # pragma: no cover

    messages.success(
        request=request,
        message=(
            f"{name_with_apostrophe(profile.get_full_name())} role "
            "has been changed to a member."
        ),
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


@login_required
def edit_profile_picture(request, profile_slug):  # pragma: no cover
    """
    Edit the picture of a user profile.

    This view allows updating the picture of a profile. It processes
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
        Renders the edit picture template or redirects to the profile
        detail page with a success message if the form is valid.
    """
    profile = Profile.objects.get(slug=profile_slug)

    profile_picture_form = profile_forms.ProfilePictureForm(
        request.POST or None,
    )

    if request.method == "POST":
        if profile_picture_form.is_valid():
            for image in request.FILES.getlist("image"):
                profile.image = image

            profile.save()

            messages.success(
                request=request,
                message="Profile's picture updated",
            )

            return redirect(profile)

    return render(
        request,
        "profiles/pages/edit_profile_picture.html",
        {
            "profile_picture_form": profile_picture_form,
        },
    )


@login_required
def edit_profile_skills(request, profile_slug):
    """
    Edit the skills details of a user profile.

    This view allows updating the skills details of a profile. It processes
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
        Renders the edit skills details template or redirects to the profile
        detail page with a success message if the form is valid.
    """
    profile = Profile.objects.get(slug=profile_slug)

    # Get skills and interests associated with the profile
    profile_skills = profile.skills.values_list(
        "skill",
        flat=True,
    )
    profile_interests = profile.interests.values_list(
        "interest",
        flat=True,
    )

    # Initialize the form with initial values
    initial_data = {
        "skills": profile_skills,
        "interests": profile_interests,
    }

    profile_skills_form = ProfileSkillsForm(
        request.POST or None,
        initial=initial_data,
    )

    if request.method == "POST":
        if profile_skills_form.is_valid():
            # Delete all profile skills and interests before saving
            ProfileSkill.objects.filter(profile=profile).delete()
            ProfileInterest.objects.filter(profile=profile).delete()

            skills = profile_skills_form.cleaned_data.get("skills")
            interests = profile_skills_form.cleaned_data.get("interests")

            for skill in skills:
                profile_skill_exists = ProfileSkill.objects.filter(
                    profile=profile,
                    skill=skill,
                )

                if profile_skill_exists.count() == 0:
                    profile_skill = ProfileSkill.objects.create(
                        profile=profile, skill=skill
                    )
                    profile_skill.save()

            for interest in interests:
                profile_interest_exists = ProfileInterest.objects.filter(
                    profile=profile,
                    interest=interest,
                )

                if profile_interest_exists.count() == 0:
                    profile_interest = ProfileInterest.objects.create(
                        profile=profile,
                        interest=interest,
                    )
                    profile_interest.save()

            messages.success(
                request,
                f"{name_with_apostrophe(profile.get_full_name())} profile updated.",
            )

            profile.check_and_complete_vocations_skills()

            return redirect(profile)

    return render(
        request,
        "profiles/pages/edit_profile_skills.html",
        {
            "profile_skills_form": profile_skills_form,
        },
    )


@login_required
def edit_profile_vocations(request, profile_slug):
    """
    Edit the vocations details of a user profile.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object used to process the request.
    profile_slug : str
        The slug of the profile to edit.

    Returns
    -------
    HttpResponse
        Renders the edit vocations details template or redirects to the profile
        detail page with a success message if the form is valid.
    """
    profile = Profile.objects.get(slug=profile_slug)

    # Get vocations and interests associated with the profile
    profile_vocations = profile.vocations.values_list(
        "vocation",
        flat=True,
    )

    # Initialize the form with initial values
    initial_data = {
        "vocations": profile_vocations,
    }

    profile_vocations_form = ProfileVocationForm(
        request.POST or None,
        initial=initial_data,
    )

    if request.method == "POST":
        if profile_vocations_form.is_valid():
            # Delete all profile vocations before saving
            ProfileVocation.objects.filter(profile=profile).delete()

            vocations = profile_vocations_form.cleaned_data.get("vocations")

            for vocation in vocations:
                profile_vocation_exists = ProfileVocation.objects.filter(
                    profile=profile,
                    vocation=vocation,
                )

                if profile_vocation_exists.count() == 0:
                    profile_vocation = ProfileVocation.objects.create(
                        profile=profile, vocation=vocation
                    )
                    profile_vocation.save()

            messages.success(
                request,
                f"{name_with_apostrophe(profile.get_full_name())} profile updated.",
            )

            profile.check_and_complete_vocations_skills()

            return redirect(profile)

    return render(
        request,
        "profiles/pages/edit_profile_vocations.html",
        {
            "profile_vocations_form": profile_vocations_form,
        },
    )


@login_required
def encrypt_profile(request, profile_slug):
    """
    Encrypt the profile's name to hide it from public view.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object containing the POST data.
    profile_slug : str
        The slug of the profile to encrypt.

    Returns
    -------
    HttpResponse
        A redirect response to the profile page with a success message
        if the profile was encrypted.
    """
    fake = Faker()
    profile = get_object_or_404(
        Profile,
        slug=profile_slug,
    )

    profile_encryption_form = profile_forms.ProfileEncryptionForm(
        request.POST or None,
    )

    if request.method == "POST":
        if profile_encryption_form.is_valid():
            last_name = fake.last_name()
            first_name = fake.first_name_male()

            if profile.gender == "female":
                first_name = fake.first_name_female()

            encryption_reason = profile_encryption_form.cleaned_data.get(
                "encryption_reason",
            )

            encryption_reason = EncryptionReason.objects.get(
                pk=encryption_reason,
            )

            ProfileEncryption.objects.create(
                profile=profile,
                last_name=last_name,
                first_name=first_name,
                encrypted_by=request.user.profile,
                encryption_reason=encryption_reason,
            )

            messages.success(
                request=request,
                message="Profiles name has been hidden from all users",
            )

            return redirect(profile.get_absolute_url())

    return render(
        request=request,
        template_name="profiles/pages/encrypt_profile.html",
        context={
            "profile_encryption_form": profile_encryption_form,
        },
    )


@login_required
def decrypt_profile(request, profile_slug):
    """
    Decrypt the profile's name to make it visible to all users.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    profile_slug : str
        The slug of the profile to decrypt.

    Returns
    -------
    HttpResponse
        A redirect response to the profile page with a success message
        if the profile was decrypted.
    """
    profile = get_object_or_404(Profile, slug=profile_slug)
    profile_encryption_exists = ProfileEncryption.objects.filter(
        profile=profile,
    ).exists()

    if profile_encryption_exists:
        profile_encryption = ProfileEncryption.objects.get(
            profile=profile,
        )

        if profile_encryption.encrypted_by != request.user.profile:
            messages.error(
                request=request,
                message="You cannot complete this action.",
            )

        else:
            profile_encryption.delete()

            messages.success(
                request=request,
                message=(
                    f"{name_with_apostrophe(profile.get_full_name())} "
                    "name is now visible to all users"
                ),
            )

    return redirect(profile)


@login_required
def edit_profile_faith_milestones(request, profile_slug):
    """
    Edit the faith milestones details of a user profile.

    This view allows updating the faith milestones details of a profile. It processes
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
        Renders the edit faith milestones details template or redirects to the profile
        detail page with a success message if the form is valid.
    """
    profile = Profile.objects.get(slug=profile_slug)

    # Get faith milestones associated with the profile
    profile_faith_milestones = profile.faith_milestones.values_list(
        "faith_milestone",
        flat=True,
    )

    # Initialize the form with initial values
    initial_data = {
        "faith_milestones": profile_faith_milestones,
    }

    profile_faith_milestones_form = ProfileFaithMilestonesForm(
        request.POST or None,
        initial=initial_data,
    )

    if request.method == "POST":
        if profile_faith_milestones_form.is_valid():
            faith_milestones = profile_faith_milestones_form.cleaned_data.get(
                "faith_milestones"
            )

            for faith_milestone in faith_milestones:
                profile_faith_milestone_exists = ProfileFaithMilestone.objects.filter(
                    profile=profile,
                    faith_milestone=faith_milestone,
                ).exists()

                if not profile_faith_milestone_exists:
                    profile_faith_milestone = ProfileFaithMilestone.objects.create(
                        profile=profile,
                        faith_milestone=faith_milestone,
                    )

                    profile_faith_milestone.save()

            messages.success(
                request,
                f"{name_with_apostrophe(profile.get_full_name())} profile updated.",
            )

            return redirect(profile)

    return render(
        request,
        "profiles/pages/edit_profile_faith_milestones.html",
        {
            "profile_faith_milestones_form": profile_faith_milestones_form,
        },
    )


@login_required
def edit_profile_level(request, profile_slug):
    """
    Edit the profile's level details.

    This view allows updating the level and optional sublevel details of a profile.
    It processes both GET and POST requests. If the request is POST and the form is valid,
    the profile is updated with the selected level and sublevel, and a success message
    is displayed.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object used to process the request.
    profile_slug : str
        The slug of the profile to edit.

    Returns
    -------
    HttpResponse
        Renders the edit profile level template or redirects to the profile detail page
        with a success message if the form is valid.
    """
    profile = get_object_or_404(Profile, slug=profile_slug)
    profile_level_form = ProfileLevelForm(request.POST or None)

    if request.method == "POST":
        level = request.POST.get("level")
        sublevel = request.POST.get("sublevel")

        if not level:
            messages.error(request, "Level ID is required.")
            return HttpResponseBadRequest("Level ID is required.")

        try:
            level_instance = get_object_or_404(Level, id=level)
        except ValueError:
            messages.error(request, "Invalid level ID.")
            return redirect(profile)

        sublevels = level_instance.sublevels.count()
        if sublevels > 0 and sublevel == "null":  # pragma: no cover
            pass
        else:
            new_profile_level = ProfileLevel.objects.create(
                profile=profile,
                level=level_instance,
            )

            try:
                if sublevel and sublevel != "null":
                    sublevel_instance = get_object_or_404(Sublevel, id=sublevel)
                    new_profile_level.sublevel = sublevel_instance
                    new_profile_level.save()

            except ValueError:  # pragma: no cover
                messages.error(request, "Invalid sublevel ID.")
                return redirect(profile)

            messages.success(request, "Level updated successfully.")
            return redirect(profile)

    context = {
        "profile_level_form": profile_level_form,
    }

    return render(
        request=request,
        template_name="profiles/pages/edit_profile_level.html",
        context=context,
    )


@login_required
def edit_profile_classifications(request, profile_slug, profile_classification_no):
    """
    Edit the profile's classification details.

    This view allows updating the classification and optional subclassification
    of a profile. It handles both GET and POST requests. In a POST request,
    it updates the profile's classification with the selected classification
    and subclassification if provided. A success or error message is displayed
    based on the outcome.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object used to process the request.
    profile_slug : str
        The slug of the profile to be edited.
    profile_classification_no : int
        The profile classification number to edit.

    Returns
    -------
    HttpResponse
        - If the request is GET, renders the edit profile classification form.
        - If the request is POST and valid, updates the profile's classification and
          subclassification and returns to the classification edit page
          with a success message.
        - If a similar classification exists or if the form data is invalid,
        an error message is displayed.
    """
    profile = get_object_or_404(Profile, slug=profile_slug)
    profile_classifications_form = ProfileClassificationForm(
        request.POST or None,
    )

    profile_classifications = ProfileClassification.objects.filter(
        profile=profile,
        no=profile_classification_no,
    )

    context = {
        "profile_classifications": profile_classifications,
        "profile_classification_no": profile_classification_no,
        "profile_classifications_form": profile_classifications_form,
    }

    if request.method == "POST":
        classification = request.POST.get("classification")
        subclassification = request.POST.get("subclassification")

        classification_instance = get_object_or_404(
            Classification,
            id=classification,
        )
        classification_subclassifications = (
            classification_instance.classification_subclassifications.count()
        )

        if (
            classification_subclassifications > 0 and subclassification == "null"
        ):  # pragma: no cover
            pass
        else:
            # Check if a similar profile classification already exists
            similar_profile_classification = ProfileClassification.objects.filter(
                profile=profile,
                no=profile_classification_no,
                classification=classification_instance,
            ).exists()

            if subclassification:
                subclassification_instance = get_object_or_404(
                    Subclassification,
                    id=subclassification,
                )

                similar_profile_classification = ProfileClassification.objects.filter(
                    profile=profile,
                    no=profile_classification_no,
                    classification=classification_instance,
                    subclassification=subclassification_instance,
                ).exists()

            if not similar_profile_classification:
                new_profile_classification = ProfileClassification.objects.create(
                    profile=profile,
                    no=profile_classification_no,
                    classification=classification_instance,
                )

                if subclassification:
                    subclassification_instance = get_object_or_404(
                        Subclassification,
                        id=subclassification,
                    )

                    new_profile_classification.subclassification = (
                        subclassification_instance
                    )
                    new_profile_classification.save()

                messages.success(
                    request=request,
                    message="Classification updated successfully.",
                )

                return render(
                    request=request,
                    template_name="classifications/pages/edit_profile_classifications.html",
                    context=context,
                )

            else:
                messages.error(
                    request=request,
                    message="A similar classification has already been assigned to this user",
                )

    return render(
        request=request,
        template_name="classifications/pages/edit_profile_classifications.html",
        context=context,
    )


@login_required
def profile_mentorships(request, profile_slug):
    """
    Display the mentorships for a specific profile.

    This view retrieves a profile based on the provided slug and renders
    the mentorships page for that profile. The context is currently empty
    but can be extended to include relevant profile mentorship data.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object used to process the request.
    profile_slug : str
        The slug of the profile whose mentorships are to be displayed.

    Returns
    -------
    HttpResponse
        Renders the mentorships page for the specified profile.
    """
    get_object_or_404(Profile, slug=profile_slug)

    context = {}

    return render(
        request=request,
        template_name="mentorships/pages/profile_mentorships_page.html",
        context=context,
    )


@login_required
def edit_profile_mentorship_areas(request, profile_slug):
    """
    Edit the mentorship areas for a specific profile.

    This view allows users to update the mentorship areas for a profile. It retrieves the
    current mentorship areas for the profile and initializes a form with this data. When
    the form is submitted, it validates the input, updates the mentorship areas, and
    displays a success message if the update is successful. If the user is not authorized
    to make changes, they are redirected with an error message.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object used to process the request.
    profile_slug : str
        The slug of the profile whose mentorship areas are to be edited.

    Returns
    -------
    HttpResponse
        Renders the edit profile mentorship areas page or redirects to the mentorships
        page of the profile's discipler if the form is successfully submitted.
    """
    profile = get_object_or_404(Profile, slug=profile_slug)

    profile_mentorship_areas = profile.mentorship_areas.values_list(
        "mentorship_area",
        flat=True,
    )

    initial_data = {
        "mentorship_areas": profile_mentorship_areas,
    }

    profile_mentorship_areas_form = ProfileMentorshipAreasForm(
        request.POST or None,
        initial=initial_data,
    )

    if request.method == "POST":
        if profile_mentorship_areas_form.is_valid():
            ProfileMentorshipArea.objects.filter(profile=profile).delete()
            mentorship_areas = profile_mentorship_areas_form.cleaned_data.get(
                "mentorship_areas"
            )
            for mentorship_area in mentorship_areas:
                if not ProfileMentorshipArea.objects.filter(
                    profile=profile, mentorship_area=mentorship_area
                ).exists():
                    ProfileMentorshipArea.objects.create(
                        profile=profile, mentorship_area=mentorship_area
                    )

            messages.success(
                request=request,
                message=(
                    (
                        f"{name_with_apostrophe(profile.get_full_name())} mentorship "
                        "areas have been updated"
                    )
                ),
            )
            return redirect(profile.get_mentorships_url())

    context = {
        "profile_mentorship_areas_form": profile_mentorship_areas_form,
    }

    return render(
        request=request,
        template_name="mentorships/pages/edit_profile_mentorships.html",
        context=context,
    )


@login_required
def move_to_sister_group(request, profile_slug, group_slug):
    """
    Move a member to a sister group.

    This view allows users to move a member from their current group
    to a sister group, which shares the same parent group. It retrieves
    the current group and initializes a form for selecting the member
    and the target group. On successful form submission, it updates the
    member's group and displays a success message.

    If the member is leading their current group, the group led by the
    member is also relocated as a child of the target group.

    Parameters
    ----------
    request : HttpRequest
        The incoming request object.
    profile_slug : str
        The slug of the profile (member) to be moved.
    group_slug : str
        The slug of the current group the member belongs to.

    Returns
    -------
    HttpResponse
        Renders the move-to-sister-group page or redirects to the target group's
        members page if the form is successfully submitted.
    """
    profile = get_object_or_404(Profile, slug=profile_slug)
    current_group = get_object_or_404(Group, slug=group_slug)

    move_group_form = MoveToSisterGroupForm(
        request.POST or None,
        leader_group=current_group,
    )

    if request.method == "POST":
        if move_group_form.is_valid():
            # Perform the action of moving the member to the sister group
            member = move_group_form.cleaned_data["member"]
            target_group = move_group_form.cleaned_data["target_group"]

            # Remove member from current group and add member to target group
            member.change_group(
                current_group=current_group,
                target_group=target_group,
            )

            notification_recipients = [
                current_group.leader,
                target_group.leader,
                member,
            ]

            group_change_notification = core_utils.create_group_change_notification(
                profile=member,
                current_group=current_group,
                target_group=target_group,
            )

            for recipient in notification_recipients:
                group_change_notification.add_recipient(recipient=recipient)

                # Send email notification
                core_emails.send_group_change_notification_email(
                    request=request,
                    profile=member,
                    current_group=current_group,
                    target_group=target_group,
                    recipient=recipient,
                )

            # If the member is leading their group
            if member.is_leading_group():
                # Relocate the member's group to be a child of the target group
                member.group_led.move_to(
                    target_group,
                    position="last-child",
                )

            messages.success(
                request=request,
                message=f"{member} has been moved to {target_group}.",
            )

            return redirect(target_group.get_members_url())

    context = {
        "profile": profile,
        "current_group": current_group,
        "move_group_form": move_group_form,
    }

    return render(
        request=request,
        template_name="profiles/pages/move_to_sister_group.html",
        context=context,
    )


@login_required
def move_to_child_group(request, profile_slug, group_slug):
    """
    Move a member to a child group.

    This view allows users to move a member from their current group
    to one of its child groups. It retrieves the current group and
    initializes a form for selecting the member and the target child group.
    On successful form submission, it updates the member's group and displays
    a success message.

    If the member is leading their current group, the group led by the member
    is also relocated as a child of the target group.

    Parameters
    ----------
    request : HttpRequest
        The incoming request object.
    profile_slug : str
        The slug of the profile (member) to be moved.
    group_slug : str
        The slug of the current group the member belongs to.

    Returns
    -------
    HttpResponse
        Renders the move-to-child-group page or redirects to the target group's
        members page if the form is successfully submitted.
    """
    profile = get_object_or_404(Profile, slug=profile_slug)
    current_group = get_object_or_404(Group, slug=group_slug)

    move_group_form = MoveToChildGroupForm(
        request.POST or None,
        leader_group=current_group,
    )

    if request.method == "POST":
        if move_group_form.is_valid():
            # Perform the action of moving the member to the child group
            member = move_group_form.cleaned_data["member"]
            target_group = move_group_form.cleaned_data["target_group"]

            # Remove member from current group and add member to target group
            member.change_group(
                current_group=current_group,
                target_group=target_group,
            )

            # Notify the current group's leader, target group's leader, and member
            notification_recipients = [
                current_group.leader,
                target_group.leader,
                member,
            ]

            # Create group change notification
            group_change_notification = core_utils.create_group_change_notification(
                profile=member,
                current_group=current_group,
                target_group=target_group,
            )

            # Add recipients to the notification and send email notifications
            for recipient in notification_recipients:
                group_change_notification.add_recipient(recipient=recipient)

                # Send email notification
                core_emails.send_group_change_notification_email(
                    request=request,
                    profile=member,
                    current_group=current_group,
                    target_group=target_group,
                    recipient=recipient,
                )

            # If the member is leading their group
            if member.is_leading_group():
                # Relocate the member's group to be a child of the target group
                member.group_led.move_to(
                    target_group,
                    position="last-child",
                )

            # Display success message
            messages.success(
                request=request,
                message=f"{member} has been moved to {target_group}.",
            )

            # Redirect to target group's members page
            return redirect(target_group.get_members_url())

    # Render the move-to-child-group page
    context = {
        "profile": profile,
        "current_group": current_group,
        "move_group_form": move_group_form,
    }

    return render(
        request=request,
        template_name="profiles/pages/move_to_child_group.html",
        context=context,
    )
