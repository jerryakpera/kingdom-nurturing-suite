"""
Views for the core application.
"""

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from kns.accounts import emails as account_emails
from kns.accounts.utils import decode_uid, verify_token
from kns.core.models import MakeLeaderActionApproval
from kns.custom_user.models import User
from kns.groups.models import Group
from kns.onboarding.models import ProfileCompletion
from kns.profiles.models import Profile

from .models import FAQ


# TODO: Remove test ignore
def index(request):  # pragma: no cover
    """
    Render the index page of the core application.

    Parameters
    ----------
    request : django.http.HttpRequest
        The HTTP request object.

    Returns
    -------
    django.http.HttpResponse
        The rendered HTML response for the index page.
    """

    if request.user.is_authenticated:
        profile_completion = None
        profile_completion_exists = ProfileCompletion.objects.filter(
            profile=request.user.profile
        ).exists()

        if profile_completion_exists:
            profile_completion = ProfileCompletion.objects.get(
                profile=request.user.profile
            )

        context = {
            "profile_completion": profile_completion,
        }

        group_led = Group.objects.filter(
            leader=request.user.profile,
        ).first()  # Get the first group led by the user, if any

        if group_led:
            context["local_groups"] = group_led.get_local_descendant_groups()[:3]

    else:
        context = {}

    return render(
        request=request,
        template_name="core/pages/index.html",
        context=context,
    )


def about_view(request):
    """
    Render the about page of the core application.

    Parameters
    ----------
    request : django.http.HttpRequest
        The HTTP request object.

    Returns
    -------
    django.http.HttpResponse
        The rendered HTML response for the about page.
    """
    context = {
        "groups_count": Group.objects.all().count(),
        "members_count": Profile.objects.all().count(),
    }

    return render(
        request=request,
        template_name="core/pages/about.html",
        context=context,
    )


def faqs_view(request):
    """
    Render the faqs page of the core application.

    Parameters
    ----------
    request : django.http.HttpRequest
        The HTTP request object.

    Returns
    -------
    django.http.HttpResponse
        The rendered HTML response for the faqs page.
    """

    faqs = FAQ.objects.all()

    context = {
        "faqs": faqs,
    }

    return render(
        request=request,
        template_name="core/pages/faqs.html",
        context=context,
    )


def submit_ticket_view(request):
    """
    Render the submit ticket page of the core application.

    Parameters
    ----------
    request : django.http.HttpRequest
        The HTTP request object.

    Returns
    -------
    django.http.HttpResponse
        The rendered HTML response for the submit ticket page.
    """
    context = {}

    return render(
        request=request,
        template_name="core/pages/submit_ticket.html",
        context=context,
    )


def contact_view(request):
    """
    Render the contact page of the core application.

    Parameters
    ----------
    request : django.http.HttpRequest
        The HTTP request object.

    Returns
    -------
    django.http.HttpResponse
        The rendered HTML response for the contact page.
    """
    context = {}

    return render(
        request=request,
        template_name="core/pages/contact.html",
        context=context,
    )


def error_404(
    request: HttpRequest,
    exception: Exception,
) -> HttpResponse:
    """
    Render the error page of the core application.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    exception : Exception
        The exception that triggered the 404 error.

    Returns
    -------
    HttpResponse
        The rendered HTML response for the error page.
    """
    context = {}

    return render(
        request,
        "404.html",
        context,
        status=404,
    )


def approve_make_leader_action(
    request,
    action_approval_id,
    uidb64,
    token,
):
    """
    View to approve a request to make a member a leader.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    action_approval_id : int
        Unique id of the MakeLeaderActionApproval item.
    uidb64 : str
        The base64-encoded UID of the user whose role is being approved.
    token : str
        The token used to validate the approval request.

    Returns
    -------
    HttpResponse
        A response indicating the result of the approval process.
    """
    uid = decode_uid(uidb64)
    user = get_object_or_404(User, pk=uid)

    if user and verify_token(user, token):
        approval_request = get_object_or_404(
            MakeLeaderActionApproval,
            id=action_approval_id,
        )

        if approval_request.status != "pending":
            messages.warning(
                request=request,
                message="This request is no longer valid and cannot be accepted.",
            )

            return redirect(approval_request.new_leader)

        # Ensure that the consumer is the leader of the created_group_for
        if approval_request.group_created_for != user.profile.group_led:
            messages.warning(
                request=request,
                message="You cannot complete this action.",
            )

            return redirect(approval_request.new_leader)

        approval_request.approve(user.profile)
        approval_request.notify_creator(request)

        # Send the set password email
        account_emails.send_set_password_email(
            request=request,
            profile=approval_request.new_leader,
        )

        messages.success(
            request=request,
            message=f"{approval_request.new_leader.get_full_name()} is now a leader.",
        )

        return redirect(approval_request.new_leader)
    else:
        messages.warning(
            request=request,
            message="You cannot complete this action",
        )

    return redirect(user.profile)


def approve_make_leader_action_notification(
    request,
    action_approval_id,
):
    """
    View to approve a request to make a member a leader via a notification.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    action_approval_id : int
        Unique id of the MakeLeaderActionApproval item.

    Returns
    -------
    HttpResponse
        A response indicating the result of the approval process.
    """
    approval_request = get_object_or_404(
        MakeLeaderActionApproval,
        id=action_approval_id,
    )

    if approval_request.status != "pending":
        messages.warning(
            request=request,
            message="This request is no longer valid and cannot be accepted.",
        )

        return redirect(approval_request.new_leader)

    # Ensure that the consumer is the leader of the created_group_for
    if approval_request.group_created_for != request.user.profile.group_led:
        messages.warning(
            request=request,
            message="You cannot complete this action.",
        )

        return redirect(approval_request.new_leader)

    approval_request.approve(request.user.profile)
    approval_request.notify_creator(request)

    # Send the set password email
    account_emails.send_set_password_email(
        request=request,
        profile=approval_request.new_leader,
    )

    messages.success(
        request=request,
        message=f"{approval_request.new_leader.get_full_name()} is now a leader.",
    )

    return redirect(approval_request.new_leader)


def reject_make_leader_action(
    request, action_approval_id, uidb64, token
):  # pragma: no cover
    """
    View to reject a request to make a member a leader.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    action_approval_id : int
        Unique id of the MakeLeaderActionApproval item.
    uidb64 : str
        The base64-encoded UID of the user whose role is being rejected.
    token : str
        The token used to validate the approval request.

    Returns
    -------
    HttpResponse
        A response indicating the result of the rejection process.
    """
    uid = decode_uid(uidb64)
    user = get_object_or_404(User, pk=uid)

    if user and verify_token(user, token):
        approval_request = get_object_or_404(
            MakeLeaderActionApproval,
            id=action_approval_id,
        )

        if approval_request.status != "pending":
            messages.warning(
                request=request,
                message="This request is no longer valid and cannot be rejected.",
            )

            return redirect(approval_request.new_leader)

        # Ensure that the consumer is the leader of the created_group_for
        if approval_request.group_created_for != user.profile.group_led:
            messages.warning(
                request=request,
                message="You cannot complete this action.",
            )

            return redirect(approval_request.new_leader)

        approval_request.reject(user.profile)
        approval_request.notify_creator(request)

        messages.success(
            request=request,
            message=(
                "You have rejected the request to make "
                f"{approval_request.new_leader.get_full_name()} "
                "a leader role."
            ),
        )
    else:
        messages.warning(
            request=request,
            message="You cannot complete this action",
        )

    return redirect(approval_request.new_leader)


def reject_make_leader_action_notification(
    request,
    action_approval_id,
):  # pragma: no cover
    """
    View to reject a request to make a member a leader via notification.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    action_approval_id : int
        Unique id of the MakeLeaderActionApproval item.

    Returns
    -------
    HttpResponse
        A response indicating the result of the rejection process.
    """

    approval_request = get_object_or_404(
        MakeLeaderActionApproval,
        id=action_approval_id,
    )

    if approval_request.status != "pending":
        messages.warning(
            request=request,
            message="This request is no longer valid and cannot be rejected.",
        )

        return redirect(approval_request.new_leader)

    # Ensure that the consumer is the leader of the created_group_for
    if approval_request.group_created_for != request.user.profile.group_led:
        messages.warning(
            request=request,
            message="You cannot complete this action.",
        )

        return redirect(approval_request.new_leader)

    approval_request.reject(request.user.profile)
    approval_request.notify_creator(request)

    messages.success(
        request=request,
        message=(
            "You have rejected the request to make "
            f"{approval_request.new_leader.get_full_name()} "
            "a leader role."
        ),
    )

    return redirect(approval_request.new_leader)
