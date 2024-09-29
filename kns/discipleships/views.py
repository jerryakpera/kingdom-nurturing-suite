"""
Views for the `discipleships` app.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.shortcuts import get_object_or_404, redirect, render

from kns.discipleships.forms import GroupMemberDiscipleForm
from kns.discipleships.models import Discipleship

from .models import Profile


@login_required
def profile_discipleships(request, profile_slug):
    """
    View to render a page displaying discipleships for a specific profile.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.
    profile_slug : str
        The slug of the profile to retrieve.

    Returns
    -------
    HttpResponse
        The rendered template with the discipleships of the specified
        profile.

    Raises
    ------
    Profile.DoesNotExist
        If no Profile with the given slug exists.
    """
    profile = get_object_or_404(Profile, slug=profile_slug)

    # Get the latest created_at for each disciple
    latest_created_at_for_disciples = Discipleship.objects.values(
        "disciple",
    ).annotate(
        latest_created_at=Max(
            "created_at",
        )
    )

    group_member_discipleships = Discipleship.objects.filter(
        discipler=profile,
        group="group_member",
        created_at__in=[
            entry["latest_created_at"] for entry in latest_created_at_for_disciples
        ],
    )
    first_12_discipleships = Discipleship.objects.filter(
        discipler=profile,
        group="first_12",
        created_at__in=[
            entry["latest_created_at"] for entry in latest_created_at_for_disciples
        ],
    )
    first_3_discipleships = Discipleship.objects.filter(
        discipler=profile,
        group="first_3",
        created_at__in=[
            entry["latest_created_at"] for entry in latest_created_at_for_disciples
        ],
    )
    sent_forth_discipleships = Discipleship.objects.filter(
        discipler=profile,
        group="sent_forth",
        created_at__in=[
            entry["latest_created_at"] for entry in latest_created_at_for_disciples
        ],
    )

    group_member_discipleship_form = GroupMemberDiscipleForm(
        request.POST,
        profile=profile,
    )

    if request.method == "POST":
        if group_member_discipleship_form.is_valid():
            # Check if the discipleship already exists
            discipleship_exists = Discipleship.objects.filter(
                disciple=group_member_discipleship_form.cleaned_data["disciple"]
            ).count()

            if discipleship_exists > 0:
                # Display a warning if the discipleship already exists
                messages.warning(
                    request=request,
                    message="This person is already a disciple",
                )
            else:
                # Create a new discipleship if it doesn't exist
                discipleship = group_member_discipleship_form.save(commit=False)

                # Assign the current user as the author and save the discipleship
                discipleship.author = request.user.profile
                discipleship.disciple = group_member_discipleship_form.cleaned_data[
                    "disciple"
                ]
                discipleship.discipler = profile
                discipleship.group = "group_member"

                discipleship.save()

                # Display a success message
                messages.success(
                    request=request,
                    message="Disciple added to your group members",
                )

    context = {
        "group_member_discipleships": group_member_discipleships,
        "first_12_discipleships": first_12_discipleships,
        "first_3_discipleships": first_3_discipleships,
        "sent_forth_discipleships": sent_forth_discipleships,
        "group_member_discipleship_form": group_member_discipleship_form,
    }

    return render(
        request=request,
        template_name="profiles/pages/profile_discipleships.html",
        context=context,
    )


@login_required
def move_to_group_member(request, discipleship_id):
    """
    Move a disciple to the 'group_member' group.

    This view moves a disciple from their current discipleship group to the 'group_member'
    group. The action is only allowed if the current user is the author of the discipleship.
    If the move is successful, a success message is displayed.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object used to process the request.
    discipleship_id : int
        The ID of the discipleship to be moved.

    Returns
    -------
    HttpResponse
        Redirects to the discipler's discipleships page with a success message if the move
        is successful, or an error message if the action is not allowed.
    """
    discipleship = get_object_or_404(Discipleship, id=discipleship_id)

    if request.user.profile != discipleship.author:
        messages.error(
            request=request,
            message="You cannot complete this action",
        )

        return redirect(discipleship.discipler.get_discipleships_url())

    group_member_discipleship = Discipleship(
        disciple=discipleship.disciple,
        discipler=discipleship.discipler,
        author=discipleship.author,
        group="group_member",
    )

    group_member_discipleship.save()

    messages.success(
        request=request,
        message=f"{discipleship.disciple.get_full_name()} moved to group members.",
    )

    return redirect(discipleship.discipler.get_discipleships_url())


@login_required
def move_to_first_12(request, discipleship_id):
    """
    Move a disciple to the 'first_12' group.

    This view moves a disciple from their current discipleship group to the 'first_12'
    group. The action is only allowed if the current user is the author of the discipleship.
    If the move is successful, a success message is displayed.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object used to process the request.
    discipleship_id : int
        The ID of the discipleship to be moved.

    Returns
    -------
    HttpResponse
        Redirects to the discipler's discipleships page with a success message if the move
        is successful, or an error message if the action is not allowed.
    """
    discipleship = get_object_or_404(Discipleship, id=discipleship_id)

    if request.user.profile != discipleship.author:
        messages.error(
            request=request,
            message="You cannot complete this action",
        )

        return redirect(discipleship.discipler.get_discipleships_url())

    first_12_discipleship = Discipleship(
        disciple=discipleship.disciple,
        discipler=discipleship.discipler,
        author=discipleship.author,
        group="first_12",
    )

    first_12_discipleship.save()

    messages.success(
        request=request,
        message=f"{discipleship.disciple.get_full_name()} moved to first 12.",
    )

    return redirect(discipleship.discipler.get_discipleships_url())


@login_required
def move_to_first_3(request, discipleship_id):
    """
    Move a disciple to the 'first_3' group.

    This view moves a disciple from their current discipleship group to the 'first_3'
    group. The action is only allowed if the current user is the author of the discipleship.
    If the move is successful, a success message is displayed.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object used to process the request.
    discipleship_id : int
        The ID of the discipleship to be moved.

    Returns
    -------
    HttpResponse
        Redirects to the discipler's discipleships page with a success message if the move
        is successful, or an error message if the action is not allowed.
    """
    discipleship = get_object_or_404(Discipleship, id=discipleship_id)

    if request.user.profile != discipleship.author:
        messages.error(
            request=request,
            message="You cannot complete this action",
        )

        return redirect(discipleship.discipler.get_discipleships_url())

    first_3_discipleship = Discipleship(
        disciple=discipleship.disciple,
        discipler=discipleship.discipler,
        author=discipleship.author,
        group="first_3",
    )

    first_3_discipleship.save()

    messages.success(
        request=request,
        message=f"{discipleship.disciple.get_full_name()} moved to first 3.",
    )

    return redirect(discipleship.discipler.get_discipleships_url())


@login_required
def move_to_sent_forth(request, discipleship_id):
    """
    Move a disciple to the 'sent_forth' group.

    This view moves a disciple from their current discipleship group to the 'sent_forth'
    group. The action is only allowed if the current user is the author of the discipleship.
    If the move is successful, a success message is displayed.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object used to process the request.
    discipleship_id : int
        The ID of the discipleship to be moved.

    Returns
    -------
    HttpResponse
        Redirects to the discipler's discipleships page with a success message if the move
        is successful, or an error message if the action is not allowed.
    """
    discipleship = get_object_or_404(Discipleship, id=discipleship_id)

    if request.user.profile != discipleship.author:
        messages.error(
            request=request,
            message="You cannot complete this action",
        )

        return redirect(discipleship.discipler.get_discipleships_url())

    sent_forth_discipleship = Discipleship(
        disciple=discipleship.disciple,
        discipler=discipleship.discipler,
        author=discipleship.author,
        group="sent_forth",
    )

    sent_forth_discipleship.save()

    messages.success(
        request=request,
        message=f"{discipleship.disciple.get_full_name()} sent forth.",
    )

    return redirect(discipleship.discipler.get_discipleships_url())
