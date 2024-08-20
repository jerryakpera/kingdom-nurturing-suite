"""
Views for the `groups` app.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from kns.groups.forms import GroupForm
from kns.groups.models import Group, GroupMember
from kns.profiles.decorators import profile_required


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
def group_detail(request, group_slug):
    """
    View function to display the details of a specific group.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    group_slug : str
        The slug of the group to display.

    Returns
    -------
    HttpResponse:
        The rendered template displaying the details of the group.
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
        template_name="groups/pages/group_detail.html",
        context=context,
    )


@login_required
@profile_required(redirect_url="/groups")
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

        On POST: Redirect to the group's detail page or re-render
        the form with errors.
    """
    profile = request.user.profile

    if profile.is_leading_group():
        messages.warning(
            request=request,
            message="You are already leading a group and cannot register a new group.",
        )

        return redirect(profile.group_led.get_absolute_url())

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

            # Redirect to the group detail page
            messages.success(
                request,
                "Group created successfully!",
            )

            return redirect(
                reverse(
                    "groups:group_detail",
                    kwargs={
                        "group_slug": group.slug,
                    },
                ),
            )
        else:
            messages.error(
                request,
                (
                    "There was an error creating the group.",
                    "Please check the form and try again.",
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
