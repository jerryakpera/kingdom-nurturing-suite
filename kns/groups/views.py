"""
Views for the `groups` app.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from kns.faith_milestones.forms import GroupFaithMilestonesForm
from kns.faith_milestones.models import GroupFaithMilestone
from kns.groups.forms import GroupForm
from kns.groups.models import Group, GroupMember
from kns.profiles.models import Profile
from kns.profiles.utils import name_with_apostrophe


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
    groups = Group.objects.all()

    context = {
        "groups": groups,
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
            group_form.save()

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
