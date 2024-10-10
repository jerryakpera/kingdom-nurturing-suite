"""
Views for the `groups` app.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from kns.core.utils import log_this
from kns.faith_milestones.forms import GroupFaithMilestonesForm
from kns.faith_milestones.models import GroupFaithMilestone
from kns.groups.forms import (
    GroupBasicFilterForm,
    GroupDemographicsFilterForm,
    GroupForm,
    GroupMembersFilterForm,
    GroupMentorshipAreasFilterForm,
    GroupSkillsInterestsFilterForm,
    GroupVocationsFilterForm,
)
from kns.groups.models import Group, GroupMember
from kns.profiles.models import Profile
from kns.profiles.utils import name_with_apostrophe

from .utils import GroupStatistics


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
    groups = None

    profile_group_in_exists = GroupMember.objects.filter(
        profile=request.user.profile,
    ).exists()
    profile_group_led_exists = Group.objects.filter(
        leader=request.user.profile,
    ).exists()

    # Add the tests for this if and else block to the test suite
    if profile_group_in_exists:  # pragma: no cover
        group_in = GroupMember.objects.get(
            profile=request.user.profile,
        ).group

        groups = group_in.get_descendants(
            include_self=True,
        )
    else:  # pragma: no cover
        if profile_group_led_exists:
            group_led = Group.objects.get(
                leader=request.user.profile,
            )
            groups = group_led.get_descendants(
                include_self=True,
            )
        else:
            groups = Group.objects.all()

    group_basic_filter_form = GroupBasicFilterForm(request.GET or None)
    group_members_filter_form = GroupMembersFilterForm(request.GET or None)
    group_demographics_filter_form = GroupDemographicsFilterForm(
        request.GET or None,
    )
    group_skills_interests_filter_form = GroupSkillsInterestsFilterForm(
        request.GET or None
    )
    group_vocations_filter_form = GroupVocationsFilterForm(
        request.GET or None,
    )
    group_mentorship_areas_filter_form = GroupMentorshipAreasFilterForm(
        request.GET or None
    )
    group_faith_milestones_form = GroupFaithMilestonesForm(
        request.GET or None,
    )

    if request.method == "GET":
        # Search functionality
        search_query = request.GET.get("search")
        if search_query:
            groups = groups.filter(Q(name__icontains=search_query))

        # Apply filters based on GroupBasicFilterForm data
        if group_basic_filter_form.is_valid():
            location_country = group_basic_filter_form.cleaned_data.get(
                "location_country"
            )
            location_city = group_basic_filter_form.cleaned_data.get("location_city")
            leader = group_basic_filter_form.cleaned_data.get("leader")

            if location_country:
                groups = groups.filter(
                    location_country=location_country,
                )
            if location_city:
                groups = groups.filter(
                    location_city__icontains=location_city,
                )
            if leader:
                groups = groups.filter(
                    Q(leader__first_name__icontains=leader)
                    | Q(leader__last_name__icontains=leader)
                )

        # Apply filters based on GroupMembersFilterForm data
        if group_members_filter_form.is_valid():
            num_members = group_members_filter_form.cleaned_data.get("num_members")
            num_leaders = group_members_filter_form.cleaned_data.get("num_leaders")
            num_skill_trainers = group_members_filter_form.cleaned_data.get(
                "num_skill_trainers"
            )
            num_movement_trainers = group_members_filter_form.cleaned_data.get(
                "num_movement_trainers"
            )
            num_mentors = group_members_filter_form.cleaned_data.get(
                "num_mentors",
            )
            num_external_persons = group_members_filter_form.cleaned_data.get(
                "num_external_persons"
            )

            # Apply filters based on member counts
            if num_members is not None:
                groups = groups.annotate(
                    num_members=Count("members"),
                ).filter(
                    num_members__gte=num_members,
                )

            if num_leaders is not None:
                groups = groups.annotate(
                    num_leaders=Count(
                        "members",
                        filter=Q(
                            members__profile__role="leader",
                        ),
                    )
                ).filter(
                    num_leaders__gte=num_leaders,
                )

            if num_external_persons is not None:
                groups = groups.annotate(
                    num_external_persons=Count(
                        "members",
                        filter=Q(
                            members__profile__role="external_person",
                        ),
                    )
                ).filter(
                    num_external_persons__gte=num_external_persons,
                )

            if num_skill_trainers is not None:
                groups = groups.annotate(
                    num_skill_trainers=Count(
                        "members",
                        filter=Q(
                            members__profile__is_skill_training_facilitator=True,
                        ),
                    )
                ).filter(num_skill_trainers__gte=num_skill_trainers)

            if num_movement_trainers is not None:
                groups = groups.annotate(
                    num_movement_trainers=Count(
                        "members",
                        filter=Q(
                            members__profile__is_movement_training_facilitator=True,
                        ),
                    )
                ).filter(num_movement_trainers__gte=num_movement_trainers)

            if num_mentors is not None:
                groups = groups.annotate(
                    num_mentors=Count(
                        "members",
                        filter=Q(
                            members__profile__is_mentor=True,
                        ),
                    )
                ).filter(num_mentors__gte=num_mentors)

            if num_external_persons is not None:
                groups = groups.annotate(
                    num_external_persons=Count(
                        "members",
                        filter=Q(
                            members__profile__role="external_person",
                        ),
                    )
                ).filter(
                    num_external_persons__gte=num_external_persons,
                )

        # Apply filters based on GroupDemographicsFilterForm data
        if group_demographics_filter_form.is_valid():
            num_male_members = group_demographics_filter_form.cleaned_data.get(
                "num_male_members"
            )
            num_female_members = group_demographics_filter_form.cleaned_data.get(
                "num_female_members"
            )
            more_male_members = group_demographics_filter_form.cleaned_data.get(
                "more_male_members"
            )
            more_female_members = group_demographics_filter_form.cleaned_data.get(
                "more_female_members"
            )

            if num_male_members is not None:
                groups = groups.annotate(
                    num_male_members=Count(
                        "members", filter=Q(members__profile__gender="male")
                    )
                ).filter(num_male_members__gte=num_male_members)
            if num_female_members is not None:
                groups = groups.annotate(
                    num_female_members=Count(
                        "members", filter=Q(members__profile__gender="female")
                    )
                ).filter(num_female_members__gte=num_female_members)

            if more_male_members and not more_female_members:
                groups = groups.annotate(
                    num_male_members=Count(
                        "members", filter=Q(members__profile__gender="male")
                    ),
                    num_female_members=Count(
                        "members", filter=Q(members__profile__gender="female")
                    ),
                ).filter(num_male_members__gt=F("num_female_members"))

            if more_female_members and not more_male_members:
                groups = groups.annotate(
                    num_male_members=Count(
                        "members", filter=Q(members__profile__gender="male")
                    ),
                    num_female_members=Count(
                        "members", filter=Q(members__profile__gender="female")
                    ),
                ).filter(num_female_members__gt=F("num_male_members"))

        # Apply filters based on GroupSkillsInterestsFilterForm data
        if group_skills_interests_filter_form.is_valid():
            skills = group_skills_interests_filter_form.cleaned_data.get("skills")
            interests = group_skills_interests_filter_form.cleaned_data.get("interests")
            unique_skills_count = group_skills_interests_filter_form.cleaned_data.get(
                "unique_skills_count"
            )
            unique_interests_count = (
                group_skills_interests_filter_form.cleaned_data.get(
                    "unique_interests_count"
                )
            )

            if skills:
                # Filter based on unique skills present in the groups
                groups = groups.filter(
                    members__profile__skills__skill__in=skills
                ).distinct()

            if interests:
                # Filter based on unique interests present in the groups
                groups = groups.filter(
                    members__profile__interests__interest__in=interests
                ).distinct()

            if unique_skills_count is not None:
                groups = groups.annotate(
                    unique_skills_count=Count(
                        "members__profile__skills",
                    )
                ).filter(
                    unique_skills_count__gte=unique_skills_count,
                )

            if unique_interests_count is not None:
                groups = groups.annotate(
                    unique_interests_count=Count(
                        "members__profile__interests",
                    )
                ).filter(
                    unique_interests_count__gte=unique_interests_count,
                )

        # Apply filters based on GroupVocationsFilterForm data
        if group_vocations_filter_form.is_valid():
            unique_vocations_count = group_vocations_filter_form.cleaned_data.get(
                "unique_vocations_count"
            )
            vocations = group_vocations_filter_form.cleaned_data.get("vocations")

            if vocations:
                groups = groups.filter(
                    members__profile__vocations__vocation__in=vocations
                ).distinct()

            if unique_vocations_count is not None:
                groups = groups.annotate(
                    unique_vocations_count=Count(
                        "members__profile__vocations",
                    )
                ).filter(
                    unique_vocations_count__gte=unique_vocations_count,
                )

        # Apply filters based on GroupMentorshipAreasFilterForm data
        if group_mentorship_areas_filter_form.is_valid():
            unique_mentorship_areas_count = (
                group_mentorship_areas_filter_form.cleaned_data.get(
                    "unique_mentorship_areas_count"
                )
            )
            mentorship_areas = group_mentorship_areas_filter_form.cleaned_data.get(
                "mentorship_areas"
            )

            if mentorship_areas:
                groups = groups.filter(
                    members__profile__mentorship_areas__mentorship_area__in=mentorship_areas
                ).distinct()

            if unique_mentorship_areas_count is not None:
                groups = groups.annotate(
                    unique_mentorship_areas_count=Count(
                        "members__profile__mentorship_areas",
                    )
                ).filter(
                    unique_mentorship_areas_count__gte=unique_mentorship_areas_count,
                )

        if group_faith_milestones_form.is_valid():
            faith_milestones = group_faith_milestones_form.cleaned_data.get(
                "faith_milestones",
            )

            if faith_milestones:
                groups = groups.filter(
                    faith_milestones__faith_milestone__in=faith_milestones,
                )

    if (
        request.user.profile.role == "leader"
        and not request.user.profile.is_leading_group()
    ):
        groups = Group.objects.none()

    # Pagination
    paginator = Paginator(groups, 5)
    page = request.GET.get("page")

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:  # pragma: no cover
        page_obj = paginator.page(paginator.num_pages)

    # Create an instance of GroupStatistics with the filtered groups
    groups_stats = GroupStatistics(groups).get_all_statistics()

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "groups_stats": groups_stats,
        "group_basic_filter_form": group_basic_filter_form,
        "group_members_filter_form": group_members_filter_form,
        "group_faith_milestones_form": group_faith_milestones_form,
        "group_vocations_filter_form": group_vocations_filter_form,
        "group_demographics_filter_form": group_demographics_filter_form,
        "group_skills_interests_filter_form": group_skills_interests_filter_form,
        "group_mentorship_areas_filter_form": group_mentorship_areas_filter_form,
    }

    return render(
        request=request,
        template_name="groups/pages/index.html",
        context=context,
    )


@login_required
def group_overview(request, group_slug):
    """
    View function to display the overview of a specific group.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    group_slug : str
        The slug of the group to display.

    Returns
    -------
    HttpResponse:
        The rendered template displaying the overviews of the group.
    """
    group = get_object_or_404(
        Group,
        slug=group_slug,
    )

    context = {
        "group": group,
        "sister_groups": group.sister_groups()[:6],
        "child_groups": group.child_groups()[:6],
    }

    return render(
        request=request,
        template_name="groups/pages/group_overview.html",
        context=context,
    )


@login_required
def register_group(request):
    """
    View function to register a new group.

    Handles GET requests by displaying the group registration form and
    POST requests by validating and saving the form data.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse:
        On GET: The rendered template displaying the form to create
        a group.

        On POST: Redirect to the group's overview page or re-render
        the form with errors.
    """
    profile = request.user.profile

    # Check if the profile is eligible to register a group
    if not profile.is_eligible_to_register_group():
        messages.error(
            request,
            (
                "You are not eligible to register a group. "
                "Please ensure your profile is complete and meets "
                "all the necessary criteria."
            ),
        )

        return redirect("groups:index")

    if request.method == "POST":
        group_form = GroupForm(
            request.POST,
            request.FILES,
        )

        if group_form.is_valid():
            group = group_form.save(commit=False)

            # Process uploaded images, if any
            for image in request.FILES.getlist("image"):  # pragma: no cover
                group.image = image

            # Assign the leader
            group.leader = profile

            # Handle the case where the profile is already a member
            # of a group
            try:
                group_member = GroupMember.objects.get(
                    profile=profile,
                )
                group.parent = group_member.group
            except GroupMember.DoesNotExist:
                pass

            # Save the group
            group.save()

            # Redirect to the group overview page
            messages.success(
                request,
                "Group created successfully!",
            )

            return redirect(
                reverse(
                    "groups:group_overview",
                    kwargs={
                        "group_slug": group.slug,
                    },
                ),
            )
    else:
        group_form = GroupForm()

    context = {
        "group_form": group_form,
    }

    return render(
        request=request,
        template_name="groups/pages/register_group.html",
        context=context,
    )


@login_required
def group_members(request, group_slug):
    """
    View function to display the members of a specific group.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    group_slug : str
        The slug of the group to display.

    Returns
    -------
    HttpResponse:
        The rendered template displaying the members of the group.
    """
    group = get_object_or_404(
        Group,
        slug=group_slug,
    )

    group_members_ids = [member.id for member in group.group_members()]
    members = Profile.objects.filter(pk__in=group_members_ids)

    context = {
        "group": group,
        "members": members,
    }

    return render(
        request=request,
        template_name="groups/pages/group_members.html",
        context=context,
    )


@login_required
def group_activities(request, group_slug):
    """
    View function to display the activities of a specific group.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    group_slug : str
        The slug of the group to display.

    Returns
    -------
    HttpResponse:
        The rendered template displaying the activities of the group.
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
        template_name="groups/pages/group_activities.html",
        context=context,
    )


@login_required
def group_subgroups(request, group_slug):
    """
    View function to display the subgroups of a specific group.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    group_slug : str
        The slug of the group to display.

    Returns
    -------
    HttpResponse:
        The rendered template displaying the subgroups of the group.
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
        template_name="groups/pages/group_subgroups.html",
        context=context,
    )


@login_required
def edit_group(request, group_slug):
    """
    View function to edit an existing group.

    Handles GET requests by displaying the group edit form pre-filled
    with the group's current data and POST requests by validating and
    saving the updated data.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    group_slug : str
        The slug of the group to edit.

    Returns
    -------
    HttpResponse:
        On GET: The rendered template displaying the form to edit
        the group.

        On POST: Redirect to the group's overview page or re-render
        the form with errors.
    """
    group = get_object_or_404(
        Group,
        slug=group_slug,
    )

    # Ensure the logged-in user is the group's leader
    if request.user.profile != group.leader:
        messages.warning(
            request=request,
            message="You do not have permission to edit this group.",
        )
        return redirect(
            "groups:group_overview",
            group_slug=group_slug,
        )

    if request.method == "POST":
        group_form = GroupForm(
            request.POST,
            request.FILES,
            instance=group,
        )

        if group_form.is_valid():
            group_form.save(commit=False)

            # Process uploaded images, if any
            for image in request.FILES.getlist("image"):  # pragma: no cover
                group.image = image

            group.save()

            messages.success(
                request=request,
                message="Group updated successfully!",
            )

            return redirect(
                "groups:group_overview",
                group_slug=group.slug,
            )
    else:
        group_form = GroupForm(instance=group)

    context = {
        "group": group,
        "group_form": group_form,
    }

    return render(
        request=request,
        template_name="groups/pages/edit_group.html",
        context=context,
    )


@login_required
def edit_group_milestones(request, group_slug):
    """
    Edit the faith milestones details of a user group.

    This view allows updating the faith milestones details of a group. It processes
    both GET and POST requests. If the request is POST and the form is valid,
    the group is updated, and a success message is displayed.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object used to process the request.
    group_slug : str
        The slug of the group to edit.

    Returns
    -------
    HttpResponse
        Renders the edit faith milestones details template or redirects to the group
        detail page with a success message if the form is valid.
    """
    group = Group.objects.get(slug=group_slug)

    # Get faith milestones associated with the group
    group_milestones = group.faith_milestones.values_list(
        "faith_milestone",
        flat=True,
    )

    # Initialize the form with initial values
    initial_data = {
        "faith_milestones": group_milestones,
    }

    group_milestones_form = GroupFaithMilestonesForm(
        request.POST or None,
        initial=initial_data,
    )

    if request.method == "POST":
        if group_milestones_form.is_valid():
            faith_milestones = group_milestones_form.cleaned_data.get(
                "faith_milestones"
            )

            for faith_milestone in faith_milestones:
                group_milestone_exists = GroupFaithMilestone.objects.filter(
                    group=group,
                    faith_milestone=faith_milestone,
                ).exists()

                if not group_milestone_exists:
                    group_milestone = GroupFaithMilestone.objects.create(
                        group=group,
                        faith_milestone=faith_milestone,
                    )

                    group_milestone.save()

            messages.success(
                request,
                f"{name_with_apostrophe(group.name)} group updated.",
            )

            return redirect(group)

    return render(
        request,
        "groups/pages/edit_group_faith_milestones.html",
        {
            "group_milestones_form": group_milestones_form,
        },
    )


@login_required
def remove_group_milestone(request, milestone_id):
    """
    Remove a milestone from a group based on its ID.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object used to process the request.
    milestone_id : int
        The ID of the GroupFaithMilestone to be removed.

    Returns
    -------
    HttpResponse
        Redirects to the group's detail page with a success message if the milestone
        was successfully removed.
    """
    # Ensure the milestone exists and get the associated GroupFaithMilestone instance
    group_milestone = get_object_or_404(
        GroupFaithMilestone,
        pk=milestone_id,
    )

    # Get the group associated with the milestone
    group = group_milestone.group

    # Delete the milestone
    group_milestone.delete()

    # Provide feedback to the user
    messages.success(
        request=request,
        message="Group milestone removed.",
    )

    # Redirect to the group's detail page
    return redirect(group.get_absolute_url())
