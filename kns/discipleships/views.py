"""
Views for the `discipleships` app.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from kns.core.utils import log_this
from kns.discipleships.forms import GroupMemberDiscipleForm
from kns.discipleships.models import Discipleship

from .forms import DiscipleshipFilterForm
from .models import Profile


@login_required
def index(request):
    """
    View to render a list of discipleships with filtering and searching functionality.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.

    Returns
    -------
    HttpResponse
        The rendered template with the filtered and searched list of discipleships.
    """
    # Instantiate the filter form
    filter_form = DiscipleshipFilterForm(request.GET)

    # Capture filter and search values from the GET request
    filter_groups = request.GET.getlist("filter_group")
    filter_groups = [group for group in filter_groups if group]

    filter_status = request.GET.get("filter_status", "")
    search_query = request.GET.get("search", "")

    # Query all discipleships
    discipleships = Discipleship.objects.all()

    if not request.user.is_visitor:
        # Get the current user's group
        user_profile = request.user.profile
        users_group = (
            user_profile.group_in.group
            if hasattr(
                user_profile,
                "group_in",
            )
            else user_profile.group_led
        )

        if users_group:  # pragma: no cover
            # Get all descendant groups of the user's led group
            descendant_groups = users_group.get_descendants(
                include_self=True,
            )

            # Filter discipleships related to the user's group and its descendants
            discipleships = discipleships.filter(
                Q(disciple__group_in__group__in=descendant_groups)
                | Q(discipler__group_in__group__in=descendant_groups)
                | Q(discipler__group_led__in=descendant_groups)
                | Q(disciple__group_led__in=descendant_groups)
            )

    # Apply search filter
    if search_query:
        discipleships = discipleships.filter(
            Q(disciple__first_name__icontains=search_query)
            | Q(disciple__last_name__icontains=search_query)
            | Q(discipler__first_name__icontains=search_query)
            | Q(discipler__last_name__icontains=search_query)
        )

    # Apply group filtering (supporting multiple groups)
    if filter_groups:
        discipleships = discipleships.filter(group__in=filter_groups)

    # Apply status filtering
    if filter_status:
        if filter_status == "ongoing":
            discipleships = discipleships.filter(
                completed_at__isnull=True,
            )
        elif filter_status == "completed":
            discipleships = discipleships.filter(
                completed_at__isnull=False,
            )

    # Pagination
    paginator = Paginator(discipleships, 6)  # Show 12 discipleships per page
    page = request.GET.get("page")

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:  # pragma: no cover
        page_obj = paginator.page(paginator.num_pages)

    # Update the context with the paginated results
    context = {
        "filter_form": filter_form,
        "search_query": search_query,
        "page_obj": page_obj,  # Use the paginated object instead of full list
    }

    return render(
        request=request,
        template_name="discipleships/pages/index.html",
        context=context,
    )


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
        template_name="discipleships/pages/profile_discipleships.html",
        context=context,
    )


@login_required
def move_to_discipleship_group(request, discipleship_id, new_group):
    """
    Move a disciple to a new discipleship group and mark the current discipleship as completed.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate the response.
    discipleship_id : int
        The ID of the current discipleship to be moved.
    new_group : str
        The name of the new group to which the disciple should be moved.

    Returns
    -------
    HttpResponse
        A redirect to the discipler's discipleships URL with a success or error message.

    Raises
    ------
    Discipleship.DoesNotExist
        If no Discipleship with the given ID exists.
    """
    discipleship = get_object_or_404(
        Discipleship,
        id=discipleship_id,
    )

    # Only allow the author of the discipleship to move the disciple
    if request.user.profile != discipleship.author:
        messages.error(
            request=request,
            message="You cannot complete this action",
        )

        return redirect(discipleship.discipler.get_discipleships_url())

    # Create a new discipleship in the specified group
    new_discipleship = Discipleship.objects.create(
        disciple=discipleship.disciple,
        discipler=discipleship.discipler,
        author=discipleship.author,
        group=new_group,
    )

    # Mark the old discipleship as completed
    discipleship.completed_at = timezone.now()
    discipleship.save()

    # Get display-friendly name for the group
    group_display = new_discipleship.group_display()
    messages.success(
        request=request,
        message=(
            f"{discipleship.disciple.get_full_name()} moved to "
            f"your {group_display} discipleship group."
        ),
    )

    return redirect(discipleship.discipler.get_discipleships_url())
